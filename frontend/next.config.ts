import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: ["192.168.1.18", "localhost:3000", "192.168.1.18:3000", "*.trycloudflare.com"]
};

export default nextConfig;
