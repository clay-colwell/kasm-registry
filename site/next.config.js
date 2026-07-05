/** @type {import('next').NextConfig} */

const nextConfig = {
  output: 'export',
  distDir: '../public',
  env: {
    name: 'Forescout KASM Repository',
    description: 'KASM Workspaces related to Forescout',
    icon: 'https://forescout.my.site.com/support/resource/1605750376000/Forescout_Logo_CCPage',
    listUrl: 'https://clay-colwell.github.io/kasm-registry/',
    contactUrl: 'https://github.com/clay-colwell/kasm-registry/issues',
  },
  reactStrictMode: true,
  basePath: '/kasm-registry/1.0',
  trailingSlash: true,
  images: {
    unoptimized: true,
  }
}

module.exports = nextConfig
