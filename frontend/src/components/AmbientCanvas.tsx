"use client";

import React, { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  z: number;
  color: string;
  baseSize: number;
  ox?: number;
  oy?: number;
  isBackground?: boolean;
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

    let centerX = width / 2;
    let centerY = height / 2;

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      centerX = width / 2;
      centerY = height / 2;
    };

    window.addEventListener("resize", handleResize);

    // Interactive mouse parallax
    const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    const handleMouseMove = (e: MouseEvent) => {
      mouse.targetX = (e.clientX - centerX) * 0.15;
      mouse.targetY = (e.clientY - centerY) * 0.15;
    };
    window.addEventListener("mousemove", handleMouseMove);

    // Initialize 3D Starfield Infinity Loop Warp
    const starCount = 450;
    const maxDepth = 1600;
    const fov = 400; // Field of view / perspective projection scale
    const stars: Star[] = [];

    const starColors = [
      "rgba(245, 158, 11, 0.8)",  // Amber/Gold
      "rgba(99, 102, 241, 0.85)", // Indigo
      "rgba(6, 182, 212, 0.8)",   // Cyan
      "rgba(168, 85, 247, 0.75)", // Purple
      "rgba(255, 255, 255, 0.9)"  // Bright White
    ];

    for (let i = 0; i < starCount; i++) {
      const isBackground = Math.random() > 0.70; // 70% tunnel warp, 30% background drift
      let ox = 0;
      let oy = 0;
      
      if (!isBackground) {
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 120 + 40; // Thickness of the infinity warp tunnel
        ox = Math.cos(angle) * radius;
        oy = Math.sin(angle) * radius;
      }

      stars.push({
        x: isBackground ? (Math.random() - 0.5) * 4000 : 0,
        y: isBackground ? (Math.random() - 0.5) * 4000 : 0,
        z: Math.random() * maxDepth,
        color: starColors[i % starColors.length],
        baseSize: isBackground ? Math.random() * 1.0 + 0.4 : Math.random() * 2.2 + 0.8,
        ox,
        oy,
        isBackground
      });
    }

    let globalRotation = 0;
    const speed = 2.6; // Warp flight speed

    const animate = () => {
      // Create a smooth trailing fade-out effect for star warp lines
      ctx.fillStyle = "rgba(6, 7, 13, 0.18)";
      ctx.fillRect(0, 0, width, height);

      // Interpolate mouse movement for smooth parallax drift
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      // Draw subtle color gradients representing space nebulae
      const nebula1 = ctx.createRadialGradient(
        centerX + mouse.x * 0.5 - 200, centerY + mouse.y * 0.5 - 100, 0,
        centerX + mouse.x * 0.5 - 200, centerY + mouse.y * 0.5 - 100, width * 0.7
      );
      nebula1.addColorStop(0, "rgba(99, 102, 241, 0.03)"); // Soft indigo glow
      nebula1.addColorStop(1, "rgba(6, 7, 13, 0)");
      ctx.fillStyle = nebula1;
      ctx.fillRect(0, 0, width, height);

      const nebula2 = ctx.createRadialGradient(
        centerX + mouse.x * 0.7 + 250, centerY + mouse.y * 0.7 + 150, 0,
        centerX + mouse.x * 0.7 + 250, centerY + mouse.y * 0.7 + 150, width * 0.6
      );
      nebula2.addColorStop(0, "rgba(245, 158, 11, 0.025)"); // Warm gold glow
      nebula2.addColorStop(1, "rgba(6, 7, 13, 0)");
      ctx.fillStyle = nebula2;
      ctx.fillRect(0, 0, width, height);

      // Increment rotation to twist the infinity loop path
      globalRotation += 0.0008;

      // Project, update, and render stars
      stars.forEach((star) => {
        // Move star closer
        star.z -= speed;

        // Reset stars that pass the screen plane (loop infinity)
        if (star.z <= 10) {
          star.z = maxDepth;
          if (!star.isBackground) {
            const angle = Math.random() * Math.PI * 2;
            const radius = Math.random() * 120 + 40;
            star.ox = Math.cos(angle) * radius;
            star.oy = Math.sin(angle) * radius;
          } else {
            star.x = (Math.random() - 0.5) * 4000;
            star.y = (Math.random() - 0.5) * 4000;
          }
        }

        let x = star.x;
        let y = star.y;

        if (!star.isBackground && star.ox !== undefined && star.oy !== undefined) {
          // Compute trajectory along Lemniscate of Bernoulli (3D figure-eight loop)
          const t = (star.z / maxDepth) * Math.PI * 2 + globalRotation * 1.5;
          const scale = 500; // Lemniscate size scale
          const denom = 1 + Math.sin(t) * Math.sin(t);
          const curveX = (scale * Math.cos(t)) / denom;
          const curveY = (scale * Math.sin(t) * Math.cos(t)) / denom;

          x = curveX + star.ox;
          y = curveY + star.oy;
        }

        // Apply a secondary global twisting rotation over depth to make it spiral
        const twistAngle = globalRotation * 0.2 + star.z * 0.0004;
        const cosR = Math.cos(twistAngle);
        const sinR = Math.sin(twistAngle);
        
        const rotatedX = x * cosR - y * sinR;
        const rotatedY = x * sinR + y * cosR;

        // Apply perspective projection with parallax drift
        const px = (rotatedX / star.z) * fov + centerX + mouse.x;
        const py = (rotatedY / star.z) * fov + centerY + mouse.y;

        // Check if star fits inside screen boundaries
        if (px >= 0 && px <= width && py >= 0 && py <= height) {
          // Size matches closeness
          const relativeDepth = (maxDepth - star.z) / maxDepth;
          const currentSize = star.baseSize * (1 + relativeDepth * 2.8);
          const opacity = Math.min(1, relativeDepth * 1.5);

          // Render glowing star particle
          ctx.beginPath();
          ctx.arc(px, py, currentSize, 0, Math.PI * 2);
          ctx.fillStyle = star.color
            .replace("0.8", `${opacity * 0.8}`)
            .replace("0.85", `${opacity * 0.85}`)
            .replace("0.9", `${opacity * 0.9}`)
            .replace("0.75", `${opacity * 0.75}`);
          ctx.fill();

          // Render speed trail line for stars near the edge (warp effect)
          if (!star.isBackground && star.z < maxDepth * 0.4) {
            ctx.beginPath();
            ctx.lineWidth = currentSize * 0.4;
            ctx.strokeStyle = star.color
              .replace("0.8", `${opacity * 0.18}`)
              .replace("0.85", `${opacity * 0.18}`)
              .replace("0.9", `${opacity * 0.22}`)
              .replace("0.75", `${opacity * 0.14}`);
            
            // Vector pointing outward from center
            const prevZ = star.z + speed * 10;
            let prevX = star.x;
            let prevY = star.y;
            
            if (star.ox !== undefined && star.oy !== undefined) {
              const prevT = (prevZ / maxDepth) * Math.PI * 2 + globalRotation * 1.5;
              const prevScale = 500;
              const prevDenom = 1 + Math.sin(prevT) * Math.sin(prevT);
              const prevCurveX = (prevScale * Math.cos(prevT)) / prevDenom;
              const prevCurveY = (prevScale * Math.sin(prevT) * Math.cos(prevT)) / prevDenom;
              prevX = prevCurveX + star.ox;
              prevY = prevCurveY + star.oy;
            }
            
            const prevTwist = globalRotation * 0.2 + prevZ * 0.0004;
            const prevRotX = prevX * Math.cos(prevTwist) - prevY * Math.sin(prevTwist);
            const prevRotY = prevX * Math.sin(prevTwist) + prevY * Math.cos(prevTwist);

            const prevPx = (prevRotX / prevZ) * fov + centerX + mouse.x;
            const prevPy = (prevRotY / prevZ) * fov + centerY + mouse.y;

            ctx.moveTo(px, py);
            ctx.lineTo(prevPx, prevPy);
            ctx.stroke();
          }
        }
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
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
