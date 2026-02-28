#!/usr/bin/env node
/**
 * 遗忘模型 - 温度模型 + GC 归档
 * 基于艾宾浩斯遗忘曲线
 */
const fs = require('fs');
const path = require('path');

const MEMORY_DIR = process.env.MEMORY_DIR || '/home/user/.openclaw/workspace/memory';
const ARCHIVE_DIR = path.join(MEMORY_DIR, '.archive');

// 温度权重
const WEIGHTS = {
    age: 0.5,
    ref: 0.3,
    pri: 0.2
};

console.log('🧠 遗忘模型计算...');

// 计算温度
function calculateTemperature(fileData) {
    // age_score: 半衰期约 23 天
    const daysSince = (Date.now() - new Date(fileData.created).getTime()) / (1000 * 60 * 60 * 24);
    const ageScore = Math.exp(-0.03 * daysSince);
    
    // ref_score: 近 7 天引用次数
    const refScore = Math.min(fileData.recentRefs / 3, 1.0);
    
    // priority_score
    const priorityScore = { '🔴': 1.0, '🟡': 0.5, '⚪': 0.0 }[fileData.priority] || 0;
    
    return WEIGHTS.age * ageScore + WEIGHTS.ref * refScore + WEIGHTS.pri * priorityScore;
}

// 归档规则
const ARCHIVE_RULES = {
    log: { maxAge: 30, protectIfReferenced: true },
    reflection: { maxAge: 30, protectIfReferenced: false },
    actions: { maxAge: 14, protectIfReferenced: false },
    decisions: { maxAge: null, protectIfReferenced: false }, // 永不归档
    lessons: { maxAge: null, priority: { '🔴': 'never', '🟡': 30, '⚪': 30 } },
    people: { maxAge: null, protectIfReferenced: false }, // 永不归档
    projects: { maxAge: null, protectIfReferenced: false },
    preferences: { maxAge: null, protectIfReferenced: false }
};

// 主函数
function runGC() {
    if (!fs.existsSync(ARCHIVE_DIR)) fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
    
    console.log('🗑️ 开始垃圾回收...\n');
    
    let archived = 0;
    let markedStale = 0;
    
    // 扫描各目录
    for (const [category, rule] of Object.entries(ARCHIVE_RULES)) {
        const dir = path.join(MEMORY_DIR, category === 'log' ? '' : category);
        if (!fs.existsSync(dir)) continue;
        
        const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
        
        for (const file of files) {
            const filePath = path.join(dir, file);
            const stats = fs.statSync(filePath);
            const age = (Date.now() - stats.mtimeMs) / (1000 * 60 * 60 * 24);
            
            // 保护规则
            if (rule.maxAge === null) continue; // 永不归档
            if (age <= rule.maxAge) continue;
            
            // 检查是否被引用
            if (rule.protectIfReferenced && isReferenced(file)) {
                console.log(`  ⏭️ 跳过 (被引用): ${file}`);
                continue;
            }
            
            // 归档
            const archivePath = path.join(ARCHIVE_DIR, file);
            fs.renameSync(filePath, archivePath);
            archived++;
            console.log(`  ✅ 归档: ${file}`);
        }
    }
    
    console.log(`\n📊 归档完成: ${archived} 个文件`);
    
    // 扫描过时
    scanStale();
}

function isReferenced(filename) {
    const dateMatch = filename.match(/\d{4}-\d{2}-\d{2}/);
    if (!dateMatch) return false;
    
    const dateStr = dateMatch[0];
    const files = fs.readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
    
    for (const f of files) {
        if (f === filename) continue;
        const content = fs.readFileSync(path.join(MEMORY_DIR, f), 'utf8');
        if (content.includes(dateStr) || content.includes(`[[${dateStr}]]`)) {
            return true;
        }
    }
    return false;
}

function scanStale() {
    console.log('\n🔍 扫描过时文件...');
    
    const knowledgeDirs = ['lessons', 'decisions', 'people'];
    
    for (const dir of knowledgeDirs) {
        const fullDir = path.join(MEMORY_DIR, dir);
        if (!fs.existsSync(fullDir)) continue;
        
        const files = fs.readdirSync(fullDir).filter(f => f.endsWith('.md'));
        
        for (const file of files) {
            const filePath = path.join(fullDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            
            // 提取 last_verified
            const match = content.match(/last_verified:\s*(\d{4}-\d{2}-\d{2})/);
            if (!match) continue;
            
            const days = (Date.now() - new Date(match[1]).getTime()) / (1000 * 60 * 60 * 24);
            
            if (days > 30) {
                // 标记过时
                const newContent = content.replace(
                    /status:\s*(\w+)/,
                    'status: ⚠️ stale'
                );
                fs.writeFileSync(filePath, newContent);
                console.log(`  ⚠️ 标记过时: ${file} (${Math.floor(days)}天)`);
            }
        }
    }
}

// CLI
const args = process.argv.slice(2);
if (args[0] === 'run' || !args[0]) {
    runGC();
}
else if (args[0] === 'temp') {
    // 测试温度计算
    const testData = {
        created: '2026-02-01',
        recentRefs: 2,
        priority: '🟡'
    };
    const temp = calculateTemperature(testData);
    console.log('测试温度:', temp);
    console.log('状态:', temp > 0.7 ? '🔥 Hot' : temp > 0.3 ? '🌤️ Warm' : '🧊 Cold');
}
