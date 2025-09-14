const fs = require("node:fs");
const path = require("node:path");

const everyApp = [];

const getLastQuery = (argv) => {
	const query = argv[argv.length - 1];
	return query;
};

const getsAllQueries = (argv) => {
	const queries = argv.slice(1);
	return queries;
};

const fetchApps = async (dir) => {
	const apps = [];
	const appDirectory = await fs.readdir(dir);
	for (const app of appDirectory) {
		const appPath = path.join(dir, app);
		if (app.endsWith(".app") && fs.statSync(appPath).isDirectory()) {
			apps.push({
				title: app,
				path: appPath,
				icon: "",
			});
		}
	}
	return apps;
};

const getAllApps = async () => {
	const appsDir = "/Applications";
	const appSetappDir = "/Applications/Setapp";
	const appsFromDir = await fetchApps(appsDir);
	console.log(appsFromDir);
	everyApp.push(...appsFromDir);
	const appsFromsetapp = await fetchApps(appSetappDir);
	console.log(appsFromsetapp);
	everyApp.push(...appsFromsetapp);
	console.log(everyApp);
};

getAllApps();
