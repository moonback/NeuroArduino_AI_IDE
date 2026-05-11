import React, { useEffect, useRef, useState } from 'react';
import { Activity, Trash2, Maximize2, Settings } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const SerialPlotter = ({ logs, onClear }) => {
    const { t } = useTranslation();
    const canvasRef = useRef(null);
    const [dataPoints, setDataPoints] = useState([]);
    const [maxPoints, setMaxPoints] = useState(100);
    const [autoScale, setAutoScale] = useState(true);

    // Extract numbers from logs
    useEffect(() => {
        const lastLog = logs[logs.length - 1];
        if (lastLog && lastLog.type === 'serial') {
            const matches = lastLog.message.match(/[-+]?[0-9]*\.?[0-9]+/g);
            if (matches) {
                const values = matches.map(Number);
                setDataPoints(prev => {
                    const next = [...prev, values];
                    if (next.length > maxPoints) return next.slice(next.length - maxPoints);
                    return next;
                });
            }
        }
    }, [logs, maxPoints]);

    // Draw logic
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        ctx.clearRect(0, 0, width, height);

        if (dataPoints.length < 2) return;

        // Find min/max for scaling
        let min = Infinity;
        let max = -Infinity;
        dataPoints.forEach(values => {
            values.forEach(v => {
                if (v < min) min = v;
                if (v > max) max = v;
            });
        });

        // Add padding to scale
        if (max === min) {
            max += 1;
            min -= 1;
        }
        const range = max - min;
        const padding = range * 0.1;
        const displayMin = min - padding;
        const displayMax = max + padding;
        const displayRange = displayMax - displayMin;

        // Draw Grid
        ctx.strokeStyle = '#30363d';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = height - (i * height / 4);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
            
            // Labels
            ctx.fillStyle = '#8b949e';
            ctx.font = '10px monospace';
            const val = displayMin + (i * displayRange / 4);
            ctx.fillText(val.toFixed(1), 5, y - 5);
        }

        // Draw Lines (multi-channel support)
        const colors = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#db61a2'];
        const numChannels = dataPoints[0].length;

        for (let ch = 0; ch < numChannels; ch++) {
            ctx.strokeStyle = colors[ch % colors.length];
            ctx.lineWidth = 2;
            ctx.beginPath();

            dataPoints.forEach((values, i) => {
                const x = (i / (maxPoints - 1)) * width;
                const val = values[ch] !== undefined ? values[ch] : 0;
                const y = height - ((val - displayMin) / displayRange) * height;
                
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
        }

    }, [dataPoints, maxPoints]);

    return (
        <div className="flex flex-col h-full w-full bg-[#0d1117] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-[#161b22] border-b border-[#30363d] select-none">
                <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-gray-400">
                    <Activity size={14} color="#58a6ff" />
                    <span>{t('serialPlotter')}</span>
                </div>

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] text-gray-500">{t('points')}</span>
                        <select 
                            value={maxPoints} 
                            onChange={e => setMaxPoints(Number(e.target.value))}
                            className="bg-[#0d1117] text-gray-300 border border-[#30363d] rounded px-1 py-0.5 text-[10px] outline-none"
                        >
                            <option value={50}>50</option>
                            <option value={100}>100</option>
                            <option value={200}>200</option>
                            <option value={500}>500</option>
                        </select>
                    </div>

                    <button
                        onClick={() => { setDataPoints([]); onClear(); }}
                        className="p-1.5 text-gray-400 hover:text-white hover:bg-white/10 rounded transition-colors"
                    >
                        <Trash2 size={14} />
                    </button>
                </div>
            </div>

            <div className="flex-1 p-4 relative bg-[#0b0f14]">
                <canvas 
                    ref={canvasRef} 
                    width={800} 
                    height={400} 
                    style={{ width: '100%', height: '100%' }}
                />
            </div>
        </div>
    );
};

export default SerialPlotter;
