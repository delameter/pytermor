# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------



html_theme_options = {
    "footer_icons": [
        {
            "name": "pypi",
            "url": "https://pypi.org/project/pytermor",
            "html": """
                <svg width="8.3862762mm" height="7.9437408mm" viewBox="0 0 8.3862762 7.9437408" version="1.1"> 
                    <g transform="translate(-70.327089,-65.242521)"><g transform="matrix(0.26458333,0,0,0.26458333,-104.4515,-52.03226)"> 
                        <path stroke-width="0.355076" d="m 660.75803,449.15562 15.55544,5.66172 15.78565,-5.74552 -15.55544,-5.66172 z" style="fill:currentColor;fill-opacity:0.4;stroke:currentColor;stroke-opacity:1.0" />
                        <path stroke-width="0.355076" d="m 676.31347,454.81734 v 18.28268 l 15.78565,-5.74551 v -18.28269 z" style="fill:currentColor;fill-opacity:0.37;stroke:currentColor;stroke-opacity:1.0" />
                        <path stroke-width="0.355076" d="m 660.75803,449.15562 15.55544,5.66172 v 18.28268 l -15.55544,-5.66171 z" style="fill:currentColor;fill-opacity:0.25;stroke:currentColor;stroke-opacity:1.0" />
                    </g></g>
                </svg>
            """,
            "class": "",
        },
        {
            "name": "github",
            "url": "https://github.com/delameter/pytermor",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "light_css_variables": {
        "color-internal-reference": "#000000",
        "color-link": "#36c",
        "color-link--hover": "var(--color-link)",
        "color-link-external": "#1ba6c7",
        "color-link-external--hover": "var(--color-link)",
        "color-link-underline": "none",
        "color-link-underline--hover": "var(--color-link)",
        "color-brand-primary": "var(--color-link)",
        "color-brand-content": "var(--color-link)",
        "color-pt-doctest-background": "#f8f8f8",
        "color-pt-doctest-border": "#f0f0f0",
        "color-pt-control-char-background": "hsla(0, 90%, 50%, .15)",
        "color-pt-class-background": "hsla(215, 100%, 95%, 0.5)",
        "color-pt-class-border": "hsl(208, 100%, 75%)",
        "color-pt-exception-background": "hsla(0, 100%, 95%, 0.5)",
        "color-pt-exception-border": "hsl(0, 50%, 60%)",
        "color-pt-module-method-background": "hsla(144, 100%, 95%, 0.5)",
        "color-pt-module-method-border": "hsl(144, 50%, 60%)",
        "color-pt-data-background": "hsla(220, 20%, 95%, 0.5)",
        "color-pt-data-border": "hsl(220, 3%, 74%)",
        "color-pt-method-background": "hsla(45, 20%, 95%, 0.5)",
        "color-pt-method-border": "hsl(45, 3%, 74%)",
        "color-pt-highlight-target-border": "hsl(50, 75%, 60%)",
        "color-pt-highlight-target-foreground": "var(--color-api-keyword)",
        "color-pt-badge-border": "none",
        "color-pt-badge-background": "none",
        "color-pt-badge-foreground": "inherit",
        "color-pt-badge-text-shadow": "inherit",
    },
    "dark_css_variables": {
        "color-internal-reference": "#ffffff",
        "color-link": "#69f",
        "color-link--hover": "var(--color-link)",
        "color-link-external": "#a5d6ff",
        "color-link-external--hover": "var(--color-link)",
        "color-link-underline": "none",
        "color-link-underline--hover": "var(--color-link)",
        "color-brand-primary": "var(--color-link)",
        "color-brand-content": "var(--color-link)",
        "color-pt-doctest-background": "#202020",
        "color-pt-doctest-border": "#282828",
        "color-pt-control-char-background": "hsla(0, 90%, 50%, .15)",
        "color-api-overall": "var(--color-foreground-secondary)",
        "color-api-name": "var(--color-foreground-primary)",
        "color-api-pre-name": "var(--color-foreground-primary)",
        "color-api-paren": "var(--color-foreground-secondary)",
        "color-api-keyword": "var(--color-foreground-primary)",
        "color-pt-class-background": "hsla(215, 70%, 25%, 0.25)",
        "color-pt-class-border": "hsla(208, 100%, 35%, 0.5)",
        "color-pt-exception-background": "hsla(0, 70%, 25%, 0.25)",
        "color-pt-exception-border": "hsla(0, 100%, 35%, 0.5)",
        "color-pt-module-method-background": "hsla(120, 70%, 25%, 0.25)",
        "color-pt-module-method-border": "hsla(143, 100%, 35%, 0.5)",
        "color-pt-data-background": "hsla(220, 10%, 35%, 0.25)",
        "color-pt-data-border": "hsla(220, 20%, 65%, 0.5)",
        "color-pt-method-background": "hsla(45, 10%, 35%, 0.25)",
        "color-pt-method-border": "hsla(45, 20%, 65%, 0.5)",
        "color-pt-highlight-target-border": "hsl(50, 75%, 60%)",
        "color-pt-highlight-target-foreground": "hsla(50, 100%, 50%, 75%)",
        "color-pt-badge-border": "inherit",
        "color-pt-badge-background": "black",
        "color-pt-badge-foreground": "inherit",
        "color-pt-badge-text-shadow": "none",
    },
}
