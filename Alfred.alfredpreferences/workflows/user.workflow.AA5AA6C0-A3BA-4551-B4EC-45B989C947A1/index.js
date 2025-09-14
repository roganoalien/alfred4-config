// WORKING EXAMPLE
import alfy from "alfy";
import fs from "node:fs";
import plist from "simple-plist";
import path from "node:path";

const regularApps = "/Applications";
const setApps = "/Applications/Setapp";
const utilities = "/Applications/Utilities";

const blackList = [
	"Adobe Acrobat DC",
	"Adobe Application Manager",
	"Adobe Creative Cloud",
	"Adobe Creative Cloud Experience",
	"Adobe Installers",
	"Adobe Sync",
	"Alfred 4.app",
	"Alfred 5.app",
];

const appsArray = [];

const readPlist = (filePath) => {
	if (fs.existsSync(filePath)) {
		const plistData = plist.readFileSync(filePath);
		return plistData.CFBundleIconFile || plistData.CFBundleTypeIconFile;
	}
	return null;
};

const assignObj = (appDir, file, iconName, location, isAdobe = false) => {
	const tempObj = {
		uid: file.replace(".app", "").replace(/\s/g, "").toLowerCase(),
		type: "app",
		autocomplete: file.replace(".app", ""),
		title: file,
		subtitle: location,
		name: file.replace(".app", ""),
		path: path.join(appDir, isAdobe ? "" : file),
		arg: file.replace(".app", ""),
		icon: {
			type: "appicon",
			path: path.join(
				appDir,
				isAdobe ? "" : file,
				"Contents",
				"Resources",
				typeof iconName === "string" && iconName.includes(".icns")
					? iconName
					: `${iconName}.icns`,
			),
		},
	};
	return {
		title: file,
		subtitle: location,
		name: file.replace(".app", ""),
		path: path.join(appDir, isAdobe ? "" : file),
		icon: {
			path: path.join(
				appDir,
				isAdobe ? "" : file,
				"Contents",
				"Resources",
				typeof iconName === "string" && iconName.includes(".icns")
					? iconName
					: `${iconName}.icns`,
			),
		},
		arg: JSON.stringify(tempObj),
	};
};

const handleInternal = (appDir, file, location, isAdobe = false) => {
	const iconName = readPlist(
		path.join(appDir, isAdobe ? "" : file, "Contents", "Info.plist"),
	);
	const obj = assignObj(appDir, file, iconName, location, isAdobe);
	appsArray.push(obj);
};

const handleAdobe = (appDir, file, location) => {
	const newAppDir = path.join(appDir, file, `${file}.app`);
	const newFile = `${file}.app`;
	handleInternal(newAppDir, newFile, location, true);
};

const addApps2Array = (appDir, location) => {
	const files = fs.readdirSync(appDir);
	if (files.length > 0) {
		for (let i = 0; i < files.length; i++) {
			if (!files[i].includes("for Safari") && !blackList.includes(files[i])) {
				if (files[i].includes("Adobe")) handleAdobe(appDir, files[i], location);
				if (files[i].includes(".app")) {
					handleInternal(appDir, files[i], location, false);
				}
			}
		}
	}
};

addApps2Array(regularApps, "/Applications");
addApps2Array(setApps, "/Setapp");
addApps2Array(utilities, "/Utilities");

const filterAndSort = () => {
	const input = alfy.input;
	if (input.length > 0 || input !== undefined) {
		const filtered = appsArray.filter((app) =>
			app.title.toLowerCase().includes(input.toLowerCase()),
		);
		return filtered.sort((a, b) => a.name.localeCompare(b.name));
	}
	return appsArray.sort((a, b) => a.name.localeCompare(b.name));
};

alfy.output(filterAndSort());
