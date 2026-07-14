/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    // Картинки блюд — векторные SVG, оптимизатор растровых изображений не нужен.
    unoptimized: true,
  },
};

export default nextConfig;
