"use client";

import React, { useEffect, useRef } from "react";

interface Node {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  vx: number;
  vy: number;
  radius: number;
  connections: number[];
  label: string;
  activation: number;
}

interface Pulse {
  path: number[]; // Indices of nodes in the path
  progress: number; // 0 to 1
  speed: number;
  color: string;
  size: number;
}

export default function AmbientCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const mouse = { x: -1000, y: -1000, active: false };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    };

    const handleMouseLeave = () => {
      mouse.active = false;
    };

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);
    window.addEventListener("resize", handleResize);

    // Multilingual words representing Ideas, Learning, Connections, Growth
    const KNOWLEDGE_WORDS = [
      "ज्ञान", "ਸਿੱਖਿਆ", "Growth", "Build", "योजना", "ਤਰੱਕੀ", "Explore", "ਸਾਂਝ",
      "विचार", "வளர்ச்சி", "Learn", "উন্নতি", "Connect", "જ્ઞાન", "சமூகம்", "Progress",
      "Creation", "సృజనాత్మకత", "कौशल", "ਸੂਝ", "Discovery", "સાથી", "বন্ধু", "தோழன்"
    ];

    // Create knowledge network nodes (slower drift)
    const nodeCount = 24;
    const nodes: Node[] = [];

    for (let i = 0; i < nodeCount; i++) {
      const x = Math.random() * width;
      const y = Math.random() * height;
      nodes.push({
        x,
        y,
        targetX: x,
        targetY: y,
        vx: (Math.random() - 0.5) * 0.04, // Exceedingly slow drift
        vy: (Math.random() - 0.5) * 0.04,
        radius: Math.random() * 1.5 + 1.2,
        connections: [],
        label: KNOWLEDGE_WORDS[i % KNOWLEDGE_WORDS.length],
        activation: 0
      });
    }

    // Connect nodes that are close to each other
    for (let i = 0; i < nodeCount; i++) {
      const n1 = nodes[i];
      const distances = nodes
        .map((n2, idx) => {
          if (idx === i) return { idx, dist: Infinity };
          const dx = n1.x - n2.x;
          const dy = n1.y - n2.y;
          return { idx, dist: Math.sqrt(dx * dx + dy * dy) };
        })
        .filter(d => d.dist < width * 0.35)
        .sort((a, b) => a.dist - b.dist);

      // Connect to top 2 nearest nodes
      const maxConnections = Math.min(2, distances.length);
      for (let j = 0; j < maxConnections; j++) {
        const destIdx = distances[j].idx;
        if (!n1.connections.includes(destIdx) && !nodes[destIdx].connections.includes(i)) {
          n1.connections.push(destIdx);
        }
      }
    }

    // Colors: Warm Gold (#f59e0b), Soft Indigo (#6366f1), Pearl Silver (#cbd5e1)
    const colors = ["#f59e0b", "#6366f1", "#cbd5e1"];

    // Initialize active pulses along paths
    const maxPulses = 6;
    const pulses: Pulse[] = [];

    const createPulse = (): Pulse | null => {
      const startCandidates = nodes.map((n, idx) => ({ n, idx })).filter(c => c.n.connections.length > 0);
      if (startCandidates.length === 0) return null;

      const start = startCandidates[Math.floor(Math.random() * startCandidates.length)];
      const nextIdx = start.n.connections[Math.floor(Math.random() * start.n.connections.length)];

      return {
        path: [start.idx, nextIdx],
        progress: 0,
        speed: Math.random() * 0.0012 + 0.0005, // Flowing connection speed
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 1.5 + 1
      };
    };

    for (let i = 0; i < maxPulses; i++) {
      const p = createPulse();
      if (p) pulses.push(p);
    }

    const animate = () => {
      // Dark deep background
      ctx.fillStyle = "rgba(6, 7, 13, 0.06)";
      ctx.fillRect(0, 0, width, height);

      // 1. Background ambient glows
      const goldGlow = ctx.createRadialGradient(
        width * 0.15, height * 0.25, 0,
        width * 0.15, height * 0.25, width * 0.5
      );
      goldGlow.addColorStop(0, "rgba(245, 158, 11, 0.015)");
      goldGlow.addColorStop(1, "rgba(6, 7, 13, 0)");
      ctx.fillStyle = goldGlow;
      ctx.fillRect(0, 0, width, height);

      const indigoGlow = ctx.createRadialGradient(
        width * 0.85, height * 0.75, 0,
        width * 0.85, height * 0.75, width * 0.5
      );
      indigoGlow.addColorStop(0, "rgba(99, 102, 241, 0.012)");
      indigoGlow.addColorStop(1, "rgba(6, 7, 13, 0)");
      ctx.fillStyle = indigoGlow;
      ctx.fillRect(0, 0, width, height);

      // 2. Update nodes and decay activation
      nodes.forEach(n => {
        n.activation = Math.max(0, n.activation - 0.008); // Slow decay

        n.targetX += n.vx;
        n.targetY += n.vy;

        if (n.targetX < 0 || n.targetX > width) n.vx *= -1;
        if (n.targetY < 0 || n.targetY > height) n.vy *= -1;

        let dispX = 0;
        let dispY = 0;

        if (mouse.active) {
          const dx = mouse.x - n.targetX;
          const dy = mouse.y - n.targetY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 200) {
            const force = (200 - dist) / 200;
            dispX = -(dx / dist) * force * 8;
            dispY = -(dy / dist) * force * 8;
          }
        }

        n.x += (n.targetX + dispX - n.x) * 0.03;
        n.y += (n.targetY + dispY - n.y) * 0.03;
      });

      // 3. Draw connection pathways
      ctx.lineWidth = 0.5;
      nodes.forEach((n1, idx1) => {
        n1.connections.forEach(idx2 => {
          const n2 = nodes[idx2];
          const grad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
          // Highlight connection lines if nodes are active
          const lineAlpha = 0.02 + (n1.activation + n2.activation) * 0.05;
          grad.addColorStop(0, `rgba(245, 158, 11, ${lineAlpha})`);
          grad.addColorStop(0.5, `rgba(99, 102, 241, ${lineAlpha * 0.8})`);
          grad.addColorStop(1, `rgba(203, 213, 225, ${lineAlpha * 0.6})`);

          ctx.strokeStyle = grad;
          ctx.beginPath();
          const midX = (n1.x + n2.x) / 2;
          const midY = (n1.y + n2.y) / 2;
          ctx.moveTo(n1.x, n1.y);
          ctx.quadraticCurveTo(midX, midY - 8, n2.x, n2.y);
          ctx.stroke();
        });
      });

      // 4. Update and draw traveling pulses
      for (let i = pulses.length - 1; i >= 0; i--) {
        const p = pulses[i];
        p.progress += p.speed;

        if (p.progress >= 1) {
          const currentEndIdx = p.path[p.path.length - 1];
          const currentNode = nodes[currentEndIdx];

          if (currentNode && currentNode.connections.length > 0) {
            const prevIdx = p.path[p.path.length - 2];
            const choices = currentNode.connections.filter(c => c !== prevIdx);
            const nextIdx = choices.length > 0 
              ? choices[Math.floor(Math.random() * choices.length)]
              : currentNode.connections[Math.floor(Math.random() * currentNode.connections.length)];

            p.path = [currentEndIdx, nextIdx];
            p.progress = 0;
          } else {
            pulses.splice(i, 1);
            const fresh = createPulse();
            if (fresh) pulses.push(fresh);
            continue;
          }
        }

        const n1 = nodes[p.path[0]];
        const n2 = nodes[p.path[1]];

        if (n1 && n2) {
          const midX = (n1.x + n2.x) / 2;
          const midY = (n1.y + n2.y) / 2;
          const t = p.progress;
          const u = 1 - t;
          const px = u * u * n1.x + 2 * u * t * midX + t * t * n2.x;
          const py = u * u * n1.y + 2 * u * t * (midY - 8) + t * t * n2.y;

          // Pulse lights up node on contact
          if (t > 0.90) {
            n2.activation = 1.0;
          }
          if (t < 0.10) {
            n1.activation = 1.0;
          }

          ctx.shadowBlur = 8;
          ctx.shadowColor = p.color;
          ctx.beginPath();
          ctx.arc(px, py, p.size, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }

      // 5. Draw faint, slowly fading/glowing words (Ideas/Connections/Growth) instead of random dots
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      nodes.forEach(n => {
        const opacity = 0.08 + n.activation * 0.45;
        const scale = 0.9 + n.activation * 0.15;
        
        ctx.font = `bold ${Math.floor(10 * scale)}px sans-serif`;
        
        if (n.activation > 0.05) {
          ctx.shadowBlur = n.activation * 6;
          ctx.shadowColor = "rgba(245, 158, 11, 0.35)";
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.fillStyle = `rgba(226, 232, 240, ${opacity})`;
        ctx.fillText(n.label, n.x, n.y);
        ctx.shadowBlur = 0;
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full z-0 pointer-events-none"
    />
  );
}
