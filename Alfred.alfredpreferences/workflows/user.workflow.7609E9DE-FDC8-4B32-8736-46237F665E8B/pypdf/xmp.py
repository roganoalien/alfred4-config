import datetime
import decimal
import re
from xml.dom.minidom import parseString

from .generic import PdfObject
from .utils import pypdfUnicode

RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"
XMP_NAMESPACE = "http://ns.adobe.com/xap/1.0/"
PDF_NAMESPACE = "http://ns.adobe.com/pdf/1.3/"
XMPMM_NAMESPACE = "http://ns.adobe.com/xap/1.0/mm/"

# What is the PDFX namespace, you might ask?  I might ask that too.  It's
# a completely undocumented namespace used to place "custom metadata"
# properties, which are arbitrary metadata properties with no semantic or
# documented meaning.  Elements in the namespace are key/value-style storage,
# where the element name is the key and the content is the value.  The keys
# are transformed into valid XML identifiers by substituting an invalid
# identifier character with \u2182 followed by the unicode hex ID of the
# original character.  A key like "my car" is therefore "my\u21820020car".
#
# \u2182, in case you're wondering, is the unicode character
# \u{ROMAN NUMERAL TEN THOUSAND}, a straightforward and obvious choice for
# escaping characters.
#
# Intentional users of the pdfx namespace should be shot on sight.  A
# custom data schema and sensical XML elements could be used instead, as is
# suggested by Adobe's own documentation on XMP (under "Extensibility of
# Schemas").
#
# Information presented here on the /pdfx/ schema is a result of limited
# reverse engineering, and does not constitute a full specification.
PDFX_NAMESPACE = "http://ns.adobe.com/pdfx/1.3/"

iso8601 = re.compile("""
        (?P<year>[0-9]{4})
        (-
            (?P<month>[0-9]{2})
            (-
                (?P<day>[0-9]+)
                (T
                    (?P<hour>[0-9]{2}):
                    (?P<minute>[0-9]{2})
                    (:(?P<second>[0-9]{2}(.[0-9]+)?))?
                    (?P<tzd>Z|[-+][0-9]{2}:[0-9]{2})
                )?
            )?
        )?
        """, re.VERBOSE)


class XmpInformation(PdfObject):
    """
    An object that represents Adobe XMP metadata. Usually accessed by
    :meth:`getXmpMetadata()<pypdf.PdfFileReader.getXmpMetadata>`
    """
    def __init__(self, stream):
        self.stream = stream
        docRoot = parseString(self.stream.getData())
        self.rdfRoot = docRoot.getElementsByTagNameNS(RDF_NAMESPACE, "RDF")[0]
        self.cache = {}

    def writeToStream(self, stream, encryption_key):
        self.stream.writeToStream(stream, encryption_key)

    def getElement(self, aboutUri, namespace, name):
        for desc in self.rdfRoot.getElementsByTagNameNS(
                RDF_NAMESPACE, "Description"
        ):
            if desc.getAttributeNS(RDF_NAMESPACE, "about") == aboutUri:
                attr = desc.getAttributeNodeNS(namespace, name)

                if attr is not None:
                    yield attr
                for element in desc.getElementsByTagNameNS(namespace, name):
                    yield element

    def getNodesInNamespace(self, aboutUri, namespace):
        for desc in self.rdfRoot.getElementsByTagNameNS(
                RDF_NAMESPACE, "Description"
        ):
            if desc.getAttributeNS(RDF_NAMESPACE, "about") == aboutUri:
                for i in range(desc.attributes.length):
                    attr = desc.attributes.item(i)

                    if attr.namespaceURI == namespace:
                        yield attr
                for child in desc.childNodes:
                    if child.namespaceURI == namespace:
                        yield child

    def _getText(self, element):
        text = ""

        for child in element.childNodes:
            if child.nodeType == child.TEXT_NODE:
                text += child.data

        return text

    def _converterString(value):
        return value

    def _converterDate(value):
        m = iso8601.match(value)
        year = int(m.group("year"))
        month = int(m.group("month") or "1")
        day = int(m.group("day") or "1")
        hour = int(m.group("hour") or "0")
        minute = int(m.group("minute") or "0")
        second = decimal.Decimal(m.group("second") or "0")
        seconds = second.to_integral(decimal.ROUND_FLOOR)
        milliseconds = (second - seconds) * 1000000
        tzd = m.group("tzd") or "Z"
        dt = datetime.datetime(
            year, month, day, hour, minute, seconds, milliseconds
        )

        if tzd != "Z":
            tzd_hours, tzd_minutes = [int(x) for x in tzd.split(":")]
            tzd_hours *= -1
            if tzd_hours < 0:
                tzd_minutes *= -1
            dt = dt + datetime.timedelta(hours=tzd_hours, minutes=tzd_minutes)

        return dt

    _test_converter_date = staticmethod(_converterDate)

    def _getterBag(namespace, name, converter):
        def get(self):
            cached = self.cache.get(namespace, {}).get(name)
            retval = []

            if cached:
                return cached

            for element in self.getElement("", namespace, name):
                bags = element.getElementsByTagNameNS(RDF_NAMESPACE, "Bag")

                if len(bags):
                    for bag in bags:
                        for item in bag.getElementsByTagNameNS(
                                RDF_NAMESPACE, "li"
                        ):
                            value = self._getText(item)
                            value = converter(value)
                            retval.append(value)

            ns_cache = self.cache.setdefault(namespace, {})
            ns_cache[name] = retval

            return retval

        return get

    def _getterSeq(namespace, name, converter):
        def get(self):
            cached = self.cache.get(namespace, {}).get(name)
            retval = []

            if cached:
                return cached

            for element in self.getElement("", namespace, name):
                seqs = element.getElementsByTagNameNS(RDF_NAMESPACE, "Seq")

                if len(seqs):
                    for seq in seqs:
                        for item in seq.getElementsByTagNameNS(
                                RDF_NAMESPACE, "li"
                        ):
                            value = self._getText(item)
                            value = converter(value)
                            retval.append(value)
                else:
                    value = converter(self._getText(element))
                    retval.append(value)

            ns_cache = self.cache.setdefault(namespace, {})
            ns_cache[name] = retval

            return retval

        return get

    def _getterLangalt(namespace, name, converter):
        def get(self):
            cached = self.cache.get(namespace, {}).get(name)
            retval = {}

            if cached:
                return cached
            for element in self.getElement("", namespace, name):
                alts = element.getElementsByTagNameNS(RDF_NAMESPACE, "Alt")
                if len(alts):
                    for alt in alts:
                        for item in alt.getElementsByTagNameNS(
                                RDF_NAMESPACE, "li"
                        ):
                            value = self._getText(item)
                            value = converter(value)
                            retval[item.getAttribute("xml:lang")] = value
                else:
                    retval["x-default"] = converter(self._getText(element))

            ns_cache = self.cache.setdefault(namespace, {})
            ns_cache[name] = retval

            return retval

        return get

    def _getterSingle(namespace, name, converter):
        def get(self):
            cached = self.cache.get(namespace, {}).get(name)

            if cached:
                return cached

            value = None

            for element in self.getElement("", namespace, name):
                if element.nodeType == element.ATTRIBUTE_NODE:
                    value = element.nodeValue
                else:
                    value = self._getText(element)
                break

            if value is not None:
                value = converter(value)

            ns_cache = self.cache.setdefault(namespace, {})
            ns_cache[name] = value

            return value

        return get

    dc_contributor = property(
        _getterBag(DC_NAMESPACE, "contributor", _converterString)
    )
    """
    Contributors to the resource (other than the authors). An unsorted array of
    names.
    """

    dc_coverage = property(
        _getterSingle(DC_NAMESPACE, "coverage", _converterString)
    )
    """
    Text describing the extent or scope of the resource.
    """

    dc_creator = property(
        _getterSeq(DC_NAMESPACE, "creator", _converterString)
    )
    """
    A sorted array of names of the authors of the resource, listed in order of
    precedence.
    """

    dc_date = property(_getterSeq(DC_NAMESPACE, "date", _converterDate))
    """
    A sorted array of dates (``datetime.datetime`` instances) of significance
    to the resource.  The dates and times are in UTC.
    """

    dc_description = property(
        _getterLangalt(DC_NAMESPACE, "description", _converterString)
    )
    """
    A language-keyed dictionary of textual descriptions of the content of the
    resource.
    """

    dc_format = property(
        _getterSingle(DC_NAMESPACE, "format", _converterString)
    )
    """
    The mime-type of the resource.
    """

    dc_identifier = property(
        _getterSingle(DC_NAMESPACE, "identifier", _converterString)
    )
    """
    Unique identifier of the resource.
    """

    dc_language = property(
        _getterBag(DC_NAMESPACE, "language", _converterString)
    )
    """
    An unordered array specifying the languages used in the resource.
    """

    dc_publisher = property(
        _getterBag(DC_NAMESPACE, "publisher", _converterString)
    )
    """
    An unordered array of publisher names.
    """

    dc_relation = property(
        _getterBag(DC_NAMESPACE, "relation", _converterString)
    )
    """
    An unordered array of text descriptions of relationships to other
    documents.
    """

    dc_rights = property(
        _getterLangalt(DC_NAMESPACE, "rights", _converterString)
    )
    """
    A language-keyed dictionary of textual descriptions of the rights the user
    has to this resource.
    """

    dc_source = property(
        _getterSingle(DC_NAMESPACE, "source", _converterString)
    )
    """
    Unique identifier of the work from which this resource was derived.
    """

    dc_subject = property(
        _getterBag(DC_NAMESPACE, "subject", _converterString)
    )
    """
    An unordered array of descriptive phrases or keywrods that specify the
    topic of the content of the resource.
    """

    dc_title = property(
        _getterLangalt(DC_NAMESPACE, "title", _converterString)
    )
    """
    A language-keyed dictionary of the title of the resource.
    """

    dc_type = property(_getterBag(DC_NAMESPACE, "type", _converterString))
    """
    An unordered array of textual descriptions of the document type.
    """

    pdf_keywords = property(
        _getterSingle(PDF_NAMESPACE, "Keywords", _converterString)
    )
    """
    An unformatted text string representing document keywords.
    """

    pdf_pdfversion = property(
        _getterSingle(PDF_NAMESPACE, "PDFVersion", _converterString)
    )
    """
    The PDF file version, for example ``1.0``, ``1.3``.
    """

    pdf_producer = property(
        _getterSingle(PDF_NAMESPACE, "Producer", _converterString)
    )
    """
    The name of the tool that created the PDF document.
    """

    xmp_createDate = property(
        _getterSingle(XMP_NAMESPACE, "CreateDate", _converterDate)
    )
    """
    The date and time the resource was originally created.  The date and time
    are returned as a UTC ``datetime.datetime`` object.
    """

    xmp_modifyDate = property(
        _getterSingle(XMP_NAMESPACE, "ModifyDate", _converterDate)
    )
    """
    The date and time the resource was last modified.  The date and time are
    returned as a UTC ``datetime.datetime`` object.
    """

    xmp_metadataDate = property(
        _getterSingle(XMP_NAMESPACE, "MetadataDate", _converterDate)
    )
    """
    The date and time that any metadata for this resource was last changed. The
    date and time are returned as a UTC ``datetime.datetime`` object.
    """

    xmp_creatorTool = property(
        _getterSingle(XMP_NAMESPACE, "CreatorTool", _converterString)
    )
    """
    The name of the first known tool used to create the resource.
    """

    xmpmm_documentId = property(
        _getterSingle(XMPMM_NAMESPACE, "DocumentID", _converterString)
    )
    """
    The common identifier for all versions and renditions of this resource.
    """

    xmpmm_instanceId = property(
        _getterSingle(XMPMM_NAMESPACE, "InstanceID", _converterString)
    )
    """
    An identifier for a specific incarnation of a document, updated each time a
    file is saved.
    """

    @property
    def custom_properties(self):
        """
        Retrieves custom metadata properties defined in the undocumented pdfx
        metadata schema.

        :return: a dictionary of key/value items for custom metadata
            properties.
        :rtype: dict
        """
        if not hasattr(self, "_custom_properties"):
            self._custom_properties = {}

            for node in self.getNodesInNamespace("", PDFX_NAMESPACE):
                key = node.localName

                while True:
                    # See documentation about PDFX_NAMESPACE earlier in file
                    idx = key.find(pypdfUnicode("\u2182"))

                    if idx == -1:
                        break

                    key = key[:idx] + chr(
                        int(key[idx + 1:idx + 5], base=16)
                    ) + key[idx+5:]
                if node.nodeType == node.ATTRIBUTE_NODE:
                    value = node.nodeValue
                else:
                    value = self._getText(node)
                self._custom_properties[key] = value

        return self._custom_properties
