#!/usr/bin/env node
/**
 * CRUD 验证机制 - 防止记忆幻觉
 */
const fs = require('fs');
const path = require('path');

const MEMORY_DIR = process.env.MEMORY_DIR || '/home/user/.openclaw/workspace/memory';

const LESSONS_DIR = path.join(MEMORY_DIR, 'lessons');
const DECISIONS_DIR = path.join(MEMORY_DIR, 'decisions');
const PEOPLE_DIR = path.join(MEMORY_DIR, 'people');

[LESSONS_DIR, DECISIONS_DIR, PEOPLE_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

class CRUDValidator {
    parseFrontmatter(content) {
        const match = content.match(/^---\n([\s\S]*?)\n---/);
        if (!match) return { fields: {}, content };
        
        const lines = match[1].split('\n');
        const fields = {};
        
        for (const line of lines) {
            const kvMatch = line.match(/^(\w+):\s*(.*)$/);
            if (kvMatch) fields[kvMatch[1]] = kvMatch[2].trim();
        }
        
        return { fields, content: content.replace(match[0], '').trim() };
    }
    
    generateFrontmatter(fields) {
        return '---\n' + 
            Object.entries(fields).map(([k, v]) => `${k}: ${v}`).join('\n') + 
            '\n---\n';
    }
    
    readKnowledgeFile(category, filename) {
        const dirMap = { lessons: LESSONS_DIR, decisions: DECISIONS_DIR, people: PEOPLE_DIR };
        const dir = dirMap[category];
        if (!dir) return null;
        
        const filePath = path.join(dir, filename);
        return fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : null;
    }
    
    isSimilar(existingContent, newContent) {
        const keywords = newContent.toLowerCase().split(/[\s,，。]/).filter(w => w.length > 2);
        const matches = keywords.filter(k => existingContent.toLowerCase().includes(k));
        return matches.length >= Math.min(3, keywords.length);
    }
    
    async validate(category, filename, newContent) {
        const existing = this.readKnowledgeFile(category, filename);
        
        if (!existing) return { action: 'ADD', reason: '新文件' };
        
        const { fields, content } = this.parseFrontmatter(existing);
        
        if (content.includes(newContent)) return { action: 'NOOP', reason: '内容已存在' };
        if (this.isSimilar(content, newContent)) return { action: 'NOOP', reason: '与现有内容相似' };
        if (fields.status === 'conflict') return { action: 'CONFLICT', reason: '存在矛盾', existing: content };
        
        return { action: 'UPDATE', reason: '新内容', existing: content, frontmatter: fields };
    }
    
    async write(category, filename, newContent, metadata = {}) {
        const result = await this.validate(category, filename, newContent);
        
        const dirMap = { lessons: LESSONS_DIR, decisions: DECISIONS_DIR, people: PEOPLE_DIR };
        const dir = dirMap[category];
        const filePath = path.join(dir, filename);
        const timestamp = new Date().toISOString().split('T')[0];
        
        if (result.action === 'NOOP') {
            console.log(`⚪ ${result.action}: ${result.reason}`);
            return result;
        }
        
        if (result.action === 'ADD' || result.action === 'UPDATE') {
            const frontmatter = {
                title: metadata.title || filename.replace('.md', ''),
                date: metadata.date || timestamp,
                category: category,
                priority: metadata.priority || '⚪',
                status: 'active',
                last_verified: timestamp
            };
            
            let content = this.generateFrontmatter(frontmatter) + '\n## 内容\n' + newContent;
            
            if (result.action === 'UPDATE') {
                content += `\n\n> [Superseded ${timestamp}]: ${(result.existing || '').slice(0, 100)}...`;
            }
            
            fs.writeFileSync(filePath, content);
            console.log(`✅ ${result.action}: 已写入 ${filename}`);
        }
        
        if (result.action === 'CONFLICT') {
            const note = `\n\n> ⚠️ CONFLICT (${timestamp}): 与上方内容矛盾\n`;
            fs.appendFileSync(filePath, note + newContent);
            console.log(`⚠️ CONFLICT: 已标记矛盾`);
        }
        
        return result;
    }
    
    verifyAll() {
        const results = [];
        
        for (const dir of [LESSONS_DIR, DECISIONS_DIR, PEOPLE_DIR]) {
            if (!fs.existsSync(dir)) continue;
            
            const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
            
            for (const file of files) {
                const content = fs.readFileSync(path.join(dir, file), 'utf8');
                const { fields } = this.parseFrontmatter(content);
                
                if (!fields.last_verified) continue;
                
                const daysSince = (Date.now() - new Date(fields.last_verified).getTime()) / (1000 * 60 * 60 * 24);
                
                if (daysSince > 30 && fields.status !== 'superseded') {
                    results.push({ file, stale: true, days: Math.floor(daysSince) });
                }
            }
        }
        return results;
    }
}

const validator = new CRUDValidator();

const args = process.argv.slice(2);
const op = args[0];

if (op === 'verify') {
    console.log('🔍 验证所有知识文件...');
    const results = validator.verifyAll();
    if (results.length === 0) {
        console.log('✅ 所有文件都是最新的');
    } else {
        console.log(`⚠️ 发现 ${results.length} 个过时的文件:`);
        results.forEach(r => console.log(`  - ${r.file} (${r.days}天未验证)`));
    }
}
else if (op === 'write') {
    validator.write(args[1] || 'lessons', args[2] || 'test.md', args[3] || '测试内容');
}
else {
    console.log('用法: node crud_validator.js verify | write <category> <filename> <content>');
}
