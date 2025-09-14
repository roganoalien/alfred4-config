require './config.rb'
require 'net/http'
require 'uri'
require 'json'

LANG_WITH_FORMALITY = ["DE", "FR", "IT", "ES", "NL", "PL", "PT-BR", "PT-PT", "PT", "JA", "RU"]

def parse(json)
  begin
    res = JSON.parse(json)
    if trans = res["translations"]
      return trans.first
    else
      return {"text" => nil, "detected_source_language" => nil}
    end
  rescue => e
    return {"text" => nil, "detected_source_language" => nil}
  end
end

def translate(query)
  if /\:fx$/ =~ query["auth_key"]
    target_uri = "https://api-free.deepl.com/v2/translate"
  else
    target_uri = "https://api.deepl.com/v2/translate"
  end

  uri = URI.parse(target_uri)
  req = Net::HTTP::Post.new(uri)

  req.set_form_data(query)
  req_options = {
    use_ssl: uri.scheme == "https"
  }

  response = Net::HTTP.start(uri.hostname, uri.port, req_options) do |http|
    http.request(req)
  end

  return parse response.body
end

def execute_query(original_text:,
                  auth_key:,
                  primary_lang:,
                  secondary_lang:,
                  mode:,
                  show_original_text:,
                  max_characters:,
                  split_sentences:,
                  preserve_formatting:,
                  formality:,
                  context:)

  # Conversion Mode
  # "translate": Lang1 to Lang2
  # "rewrite": Lang1 to Lang2 then lang 1 back again
  mode = mode || "translate"

  # Show Original Text
  # "true"
  # "false"
  show_original_text = show_original_text == "true" ? true : false

  max_characters = max_characters ? max_characters.to_i : 1000

  # Split Mode
  # "0": no split
  # "1": splits on interpunction and newlines
  # "nonewlines": splits on interpunction only
  split_sentences = split_sentences.strip || "0"

  # Preserve Fromatting
  # "0": default
  # "1": respects original formatting
  preserve_formatting = preserve_formatting.strip || "0"

  # Formality (only available in limited languages)
  # "default"
  # "more"
  # "less"
  # "prefer_more"
  # "prefer_less"
  formality = formality.strip || "default"

  # original_text = `pbpaste | textutil -convert txt -stdin -stdout`.strip

  if original_text.length > max_characters.to_i
    print "❗️ ERROR: Input text contains #{original_text.length} characters; max number of characters is set to #{max_characters}"
    exit
  elsif /\A\s*\z/ =~ original_text
    print "❗️ ERROR: Input text is empty"
  end

  intermediate = ""
  results = ""
  begin
    source = primary_lang.strip
    target = secondary_lang.strip

    query = {
      "auth_key" => auth_key,
      "text" => original_text,
      "target_lang" => target,
      "split_sentences" => split_sentences,
      "preserve_formatting" => preserve_formatting,
      "context" => context
    }

    if mode == "translate"
      if LANG_WITH_FORMALITY.include? target
        query["formality"] = formality
      end
    end

    res = translate(query)

    if res["detected_source_language"] != source
      source = secondary_lang
      target = primary_lang
      query["source_lang"] = source
      query["target_lang"] = target
      res = translate(query)
    end

    case mode
    when "translate"
      results << original_text + "\n\n" if show_original_text
      results << res["text"]
    when "rewrite"
      intermediate = res["text"]
      reversed_source = target
      reversed_target = source
      query["text"] = intermediate
      query["source_lang"] = reversed_source
      query["target_lang"] = reversed_target

      if LANG_WITH_FORMALITY.include? reversed_target
        query["formality"] = formality
      end

      new_res = translate(query)
      results << original_text + "\n\n" if show_original_text
      results << intermediate + "\n\n" + new_res["text"]
    end
  rescue => e
    results = "❗️ ERROR: " + e.to_s
  end

  print results
end
