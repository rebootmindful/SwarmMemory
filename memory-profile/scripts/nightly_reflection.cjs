#!/usr/bin/env node
/**
 * 夜间反思流程 - 记忆整合核心环节
 * 每天 23:45 自动执行
 */
const fs = require('fs');
const path = require('path');

const MEMORY_DIR = process.env.MEMORY_DIR || '/home/user/.openclaw/workspace/memory';
const TODAY = new Date().toISOString().split('T')[0];

console.log('🌙 开始夜间反思...');
console.log('日期:', TODAY);

// 1. 读取今日日志
const todayLog = path.join(MEMORY_DIR, `${TODAY}.md`);
const reflectionsDir = path.join(MEMORY_DIR, 'reflections');

if (!fs.existsSync(reflectionsDir)) fs.mkdirSync(reflectionsDir, { recursive: true });

let logContent = '';
if (fs.existsSync(todayLog)) {
    logContent = fs.readFileSync(todayLog, 'utf8');
    console.log('✅ 读取今日日志');
} else {
    console.log('⚠️ 今日无日志');
}

// 2. 生成反思内容
const reflection = generateReflection(logContent);

// 3. 写入反思文件
const reflectionFile = path.join(reflectionsDir, `${TODAY}.md`);
fs.writeFileSync(reflectionFile, reflection);
console.log('✅ 写入反思到 reflections/');

// 4. 更新 INDEX.md
updateIndex(reflection);

console.log('✅ 夜间反思完成!');

function generateReflection(logContent) {
    const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    
    // 提取今日条目
    const entries = logContent.match(/### \d{2}:\d{2} — (.+)/g) || [];
    
    let content = `# ${TODAY} 夜间反思\n\n`;
    content += `> 生成时间: ${now}\n\n`;
    content += '## 今日事件\n\n';
    
    entries.forEach(e => {
        content += `- ${e.replace('### ', '')}\n`;
    });
    
    content += '\n## 计划 vs 实际\n\n';
    content += '- 计划完成: \n';
    content += '- 实际完成: \n\n';
    content += '## 做得好的\n\n';
    content += '- \n\n';
    content += '## 需要改进的\n\n';
    content += '- \n\n';
    content += '## 学到的新知识\n\n';
    content += '- \n\n';
    content += '## 明天要改变的\n\n';
    content += '- \n\n';
    content += '---\n';
    content += '*此反思由自动脚本生成*\n';
    
    return content;
}

function updateIndex(reflection) {
    const indexFile = path.join(MEMORY_DIR, 'INDEX.md');
    
    let indexContent = '';
    if (fs.existsSync(indexFile)) {
        indexContent = fs.readFileSync(indexFile, 'utf8');
    } else {
        indexContent = `# Memory Index\n\n## Reflections\n\n| 日期 | 状态 |\n|------|------|\n`;
    }
    
    // 添加今天的反思
    const newLine = `| [[${TODAY}]] | ✅ active |\n`;
    
    if (!indexContent.includes(`[[${TODAY}]]`)) {
        indexContent += newLine;
        fs.writeFileSync(indexFile, indexContent);
        console.log('✅ 更新 INDEX.md');
    }
}
