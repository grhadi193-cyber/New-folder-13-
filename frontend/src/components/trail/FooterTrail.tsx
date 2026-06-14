'use client';

import { motion } from 'framer-motion';
import { useUserTrailStore } from '@/lib/store/user-trail';

export default function FooterTrail() {
  const getHistory = useUserTrailStore((s) => s.getHistory);
  const history = getHistory();

  if (history.length === 0) return null;

  const recent = history.slice(-5);

  return (
    <div className="flex items-center gap-0 justify-center">
      {recent.map((entry, i) => {
        const isLast = i === recent.length - 1;
        return (
          <div key={entry.path} className="flex items-center">
            {i > 0 && (
              <svg width="24" height="8" className="mx-0.5 flex-shrink-0">
                <line
                  x1="0"
                  y1="4"
                  x2="24"
                  y2="4"
                  stroke="#374151"
                  strokeWidth="1.5"
                  strokeDasharray="3 2"
                />
              </svg>
            )}
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.08 }}
              className="flex flex-col items-center gap-1"
            >
              <span
                className={`block w-2 h-2 rounded-full ${
                  isLast ? 'bg-[#10b981]' : 'bg-[#1e3a5f]'
                }`}
              />
              <span className="text-[10px] text-gray-500 whitespace-nowrap max-w-[60px] truncate">
                {entry.label}
              </span>
            </motion.div>
          </div>
        );
      })}
    </div>
  );
}
