import { useEffect, useRef } from "react";

function createBall(width, height) {
  const palette = ["#FF69B4", "#FF8FD8", "#FFFFFF", "#FFC7EA"];
  return {
    x: Math.random() * width,
    y: Math.random() * height,
    radius: 6 + Math.random() * 12,
    vx: -1.5 + Math.random() * 3,
    vy: -1.5 + Math.random() * 3,
    color: palette[Math.floor(Math.random() * palette.length)]
  };
}

export default function BouncingBalls({ ballCount = 18 }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return undefined;
    }

    const context = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;

    let width = canvas.clientWidth * dpr;
    let height = canvas.clientHeight * dpr;
    canvas.width = width;
    canvas.height = height;

    const balls = Array.from({ length: ballCount }, () => createBall(width, height));

    const resize = () => {
      width = canvas.clientWidth * dpr;
      height = canvas.clientHeight * dpr;
      canvas.width = width;
      canvas.height = height;
    };

    const step = () => {
      context.clearRect(0, 0, width, height);

      balls.forEach((ball) => {
        ball.x += ball.vx;
        ball.y += ball.vy;

        if (ball.x + ball.radius > width || ball.x - ball.radius < 0) {
          ball.vx *= -1;
        }
        if (ball.y + ball.radius > height || ball.y - ball.radius < 0) {
          ball.vy *= -1;
        }

        context.beginPath();
        context.fillStyle = ball.color;
        context.globalAlpha = 0.85;
        context.shadowColor = ball.color;
        context.shadowBlur = 16;
        context.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        context.fill();
        context.shadowBlur = 0;
      });

      animationRef.current = requestAnimationFrame(step);
    };

    animationRef.current = requestAnimationFrame(step);
    window.addEventListener("resize", resize);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener("resize", resize);
    };
  }, [ballCount]);

  return <canvas ref={canvasRef} className="bouncing-balls" aria-hidden="true" />;
}
