/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

const util = require('util');
const cp = require('child_process');
const execFile = util.promisify(cp.exec);
const os = require('os');
const platform = os.platform().toLowerCase();
const { readdirSync, existsSync } = require('fs');
const { resolve } = require('path');
const srcUrl = resolve(__dirname, '../src/');
const getExecShell = () => {
  switch (process.env.execMode) {
    case 'install':
      return 'sh webpack/npm-install-all.sh';
    case 'update':
      return 'sh webpack/npm-update.sh';
    case 'move':
      return 'sh webpack/move-build-file.sh';
    case 'change':
      return 'node webpack/change-modules-code.js';
    default:
      console.error('未获取execMode环境变量');
      process.exit(1);
  }
};

const execShellFiles = async () => {
  console.log(`【${platform}】 execMode: ${process.env.execMode}`);
  if (['darwin', 'linux'].includes(platform)) {
    const { stdout, stderr } = await execFile(getExecShell()).catch((err) => {
      console.log(`执行${process.env.execMode}出错了`);
      console.error(err);
      process.exit(1);
    });
    stdout && console.log(`stdout: ${stdout}`);
    stderr && console.log(`stderr: ${stderr}`);
    console.log('执行完成');
  } else if (platform === 'win32') {
    if (process.env.execMode === 'install') {
      readdirSync(srcUrl).forEach((mod) => {
        const packageUrl = resolve(srcUrl, mod, './package.json');
        if (mod && !mod.includes('node_modules') && existsSync(packageUrl)) {
          const cmd = /^win/.test(platform) ? 'npm.cmd' : 'npm';
          cp.spawn(cmd, ['i', '--no-audit', `--prefix ${resolve(srcUrl, mod)}`], {
            env: process.env,
            cwd: resolve(srcUrl, mod),
            stdio: 'inherit',
          });
        }
      });
    } else {
      console.error(`系统 【${platform}】 暂不兼容该命令`);
      process.exit(1);
    }
  } else {
    console.error(`系统 【${platform}】 暂不兼容该命令`);
    process.exit(1);
  }
};
execShellFiles();