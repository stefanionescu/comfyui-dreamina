import '#web/interface.css';
import { requestLocal } from '#web/http.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { message } from '#web/text.ts';

import { app } from '../../scripts/app.js';

app.registerExtension({
    name: 'dreamina',
    setup: () => {
        const stylesheet = document.createElement('link');
        stylesheet.rel = 'stylesheet';
        stylesheet.href = new URL('extension.css', import.meta.url).href;
        const stylesheets = new Set();
        for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
            stylesheets.add(link.getAttribute('href'));
        }
        if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
    },
    commands: [
        {
            id: 'dreamina.OpenSettings',
            label: message('settings.menu'),
            function: openSettings.bind(null, requestLocal),
        },
    ],
    menuCommands: [
        {
            path: ['Extensions', 'Dreamina'],
            commands: ['dreamina.OpenSettings'],
        },
    ],
});
