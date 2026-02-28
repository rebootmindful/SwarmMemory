#!/usr/bin/env node
/**
 * Memory Profile System - 统一解析 + 分层存储 + 学习能力
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const MEMORY_FILE = '/home/user/.openclaw/skills/memory-profile/MEMORY.json';

class MemorySystem {
    constructor() {
        this.data = null;
        this.load();
    }
    
    load() {
        try {
            const content = fs.readFileSync(MEMORY_FILE, 'utf8');
            this.data = JSON.parse(content);
        } catch (err) {
            this.data = this.initDefault();
            this.save();
        }
    }
    
    initDefault() {
        return {
            version: '2.1',
            meta: {
                created: new Date().toISOString(),
                updated: new Date().toISOString(),
                format: 'json'
            },
            layers: {
                L0: { events: [], maxSize: 100 },
                L1: { events: [], maxSize: 500 },
                L2: { events: [], entities: [], patterns: [], preferences: {} }
            },
            learning: {
                preferences: {},
                patterns: [],
                stats: { totalEvents: 0, lastUpdate: null }
            }
        };
    }
    
    save() {
        this.data.meta.updated = new Date().toISOString();
        fs.writeFileSync(MEMORY_FILE, JSON.stringify(this.data, null, 2));
    }
    
    addEvent(type, content, metadata = {}) {
        const event = {
            id: crypto.randomUUID(),
            type,
            content,
            metadata,
            timestamp: new Date().toISOString()
        };
        
        this.data.layers.L0.events.push(event);
        this.data.layers.L1.events.push(event);
        this.data.layers.L2.events.push(event);
        
        this.data.learning.stats.totalEvents++;
        this.data.learning.stats.lastUpdate = new Date().toISOString();
        
        this.learn(event);
        this.compress();
        this.save();
        
        return event;
    }
    
    compress() {
        if (this.data.layers.L0.events.length > this.data.layers.L0.maxSize) {
            this.data.layers.L0.events = this.data.layers.L0.events.slice(-this.data.layers.L0.maxSize);
        }
        if (this.data.layers.L1.events.length > this.data.layers.L1.maxSize) {
            this.data.layers.L1.events = this.data.layers.L1.events.slice(-this.data.layers.L1.maxSize);
        }
    }
    
    learn(event) {
        this.learnPreferences(event);
        this.learnPatterns(event);
    }
    
    learnPreferences(event) {
        const content = event.content || '';
        const type = event.type;
        
        const keywords = this.extractKeywords(content);
        
        if (!this.data.learning.preferences[type]) {
            this.data.learning.preferences[type] = { keywords: {}, count: 0 };
        }
        
        this.data.learning.preferences[type].count++;
        
        for (const kw of keywords) {
            this.data.learning.preferences[type].keywords[kw] = 
                (this.data.learning.preferences[type].keywords[kw] || 0) + 1;
        }
    }
    
    learnPatterns(event) {
        const hour = new Date(event.timestamp).getHours();
        const existing = this.data.learning.patterns.find(p => p.type === 'time_of_day');
        
        if (existing) {
            existing.data[hour] = (existing.data[hour] || 0) + 1;
        } else {
            this.data.learning.patterns.push({ type: 'time_of_day', data: { [hour]: 1 } });
        }
    }
    
    extractKeywords(text) {
        if (!text) return [];
        const words = text.toLowerCase()
            .replace(/[^\u4e00-\u9fa5a-z0-9]/g, ' ')
            .split(/\s+/)
            .filter(w => w.length > 1);
        const stopWords = new Set(['the', 'is', 'are', '的', '是', '在', '了', '和']);
        return words.filter(w => !stopWords.has(w)).slice(0, 10);
    }
    
    query(keyword, layer = 'L1') {
        const events = this.data.layers[layer].events;
        return events.filter(e => e.content && e.content.toLowerCase().includes(keyword.toLowerCase()));
    }
    
    getStats() {
        return {
            L0: this.data.layers.L0.events.length,
            L1: this.data.layers.L1.events.length,
            L2: this.data.layers.L2.events.length,
            totalEvents: this.data.learning.stats.totalEvents,
            preferences: Object.keys(this.data.learning.preferences).length,
            patterns: this.data.learning.patterns.length
        };
    }
}

// CLI
const memory = new MemorySystem();

const args = process.argv.slice(2);
const op = args[0];

if (op === 'add') {
    const event = memory.addEvent(args[1] || 'default', args[2] || '');
    console.log('✅ 添加事件:', event.id);
} 
else if (op === 'stats') {
    const stats = memory.getStats();
    console.log('📊 统计:');
    console.log('   L0 (即时):', stats.L0);
    console.log('   L1 (短期):', stats.L1);
    console.log('   L2 (长期):', stats.L2);
    console.log('   总事件:', stats.totalEvents);
    console.log('   偏好类型:', stats.preferences);
    console.log('   模式:', stats.patterns);
}
else if (op === 'prefs') {
    console.log('📝 偏好:', JSON.stringify(memory.data.learning.preferences, null, 2));
}
else if (op === 'patterns') {
    console.log('🔍 模式:', JSON.stringify(memory.data.learning.patterns, null, 2));
}
else {
    const stats = memory.getStats();
    console.log('🧠 Memory Profile System');
    console.log('=' * 40);
    console.log('L0 (即时):', stats.L0);
    console.log('L1 (短期):', stats.L1);
    console.log('L2 (长期):', stats.L2);
    console.log('总事件:', stats.totalEvents);
}
