import { Config } from '@remotion/cli/config';
import fs from 'fs';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
const macChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (fs.existsSync(macChrome)) {
  Config.setBrowserExecutable(macChrome);
}
Config.setChromiumDisableWebSecurity(true);
Config.setConcurrency(2);
