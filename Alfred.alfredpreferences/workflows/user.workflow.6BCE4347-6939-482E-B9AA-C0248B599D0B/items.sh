#!/bin/zsh

if ./desktop-icons-visible; then
  toggle_icons_title="Toggle Desktop Icons: Hide"
  toggle_icons_subtitle="Hide clutter on your Desktop."
  toggle_icons_icon_path="hide-desktop-icons.png"
else
  toggle_icons_title="Toggle Desktop Icons: Show"
  toggle_icons_subtitle="Show previously hidden icons on your Desktop."
  toggle_icons_icon_path="show-desktop-icons.png"
fi

cat <<EOF
{
	"items": [
		{
			"title": "Show ColorSlurp Window",
			"subtitle": "Show Window",
			"arg": "show-window",
			"icon": {
				"path": "icons/cs-window.png"
			},
			"uid": "show-window"
		},
		{
			"title": "Show Magnifier",
			"subtitle": "Show Magnifier",
			"arg": "show-magnifier",
			"icon": {
				"path": "icons/cs-magnifier.png"
			},
			"uid": "show-magnifier"
		},
		{
			"title": "Show Picker",
			"subtitle": "Show Picker",
			"arg": "show-picker",
			"icon": {
				"path": "icons/cs-picker.png"
			},
			"uid": "show-picker"
		},
		{
			"title": "Show Contrast",
			"subtitle": "Show Contrast",
			"arg": "show-contrast",
			"icon": {
				"path": "icons/cs-contrast.png"
			},
			"uid": "show-contrast"
		},
		{
			"title": "Show Palettes",
			"subtitle": "Show Palettes",
			"arg": "show-palettes",
			"icon": {
				"path": "icons/cs-palettes.png"
			},
			"uid": "show-palettes"
		},
		{
			"title": "Show Settings",
			"subtitle": "Show Settings",
			"arg": "show-window",
			"icon": {
				"path": "icons/cs-settings.png"
			},
			"uid": "show-settings"
		}
	]
}
EOF