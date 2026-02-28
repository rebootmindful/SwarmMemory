#!/usr/bin/env node
const fs = require('fs');

const MEMORY_FILE = '/home/user/.openclaw/skills/memory-profile/MEMORY.json';
const SYNC_STATE_FILE = '/home/user/.openclaw/skills/memory-profile/sync_state.json';

class IncrementalSync {
    constructor() {
        try {
            this.state = JSON.parse(fs.readFileSync(SYNC_STATE_FILE, 'utf8'));
        } catch {
            this.state = { lastSync: null, lastEventId: null, version: 0 };
        }
    }
    
    saveState() {
        fs.writeFileSync(SYNC_STATE_FILE, JSON.stringify(this.state, null, 2));
    }
    
    sync() {
        console.log('🔄 开始增量同步...');
        
        const memory = JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
        const events = memory.layers.L2.events;
        
        if (events.length === 0) {
            console.log('✅ 无新数据');
            return;
        }
        
        this.state.lastSync = new Date().toISOString();
        this.state.lastEventId = events[events.length - 1].id;
        this.state.version++;
        this.saveState();
        
        console.log(`✅ 同步完成: ${events.length} 个事件`);
        console.log(`   版本: ${this.state.version}`);
    }
}

const sync = new IncrementalSync();
sync.sync();
