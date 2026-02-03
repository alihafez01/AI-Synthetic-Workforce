# AI Synthetic Workforce - Frontend

Next.js 15+ frontend application for the AI Synthetic Workforce platform.

## Prerequisites

- Node.js 18.17 or higher
- pnpm (recommended) or npm

### Install pnpm (if not already installed)

```bash
npm install -g pnpm
```

## Installation

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies using pnpm
pnpm install

# Or if using npm
npm install
```

### 2. Environment Configuration

Create a .env.local file in the rontend/ directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Synthetic Workforce
```

### 3. Run Development Server

```bash
# Using pnpm
pnpm dev

# Or using npm
npm run dev
```

Application will be available at: http://localhost:3000

## Available Scripts

### Development
```bash
pnpm dev
```
Runs the development server with hot reload.

### Build
```bash
pnpm build
```
Creates an optimized production build.

### Production
```bash
pnpm start
```
Runs the production build server.

### Linting
```bash
pnpm lint
```
Runs ESLint to check code quality.

### Type Checking
```bash
pnpm type-check
```
Runs TypeScript compiler to check types.

## Project Structure

```
frontend/
├── src/
│   └── app/                   # Next.js app directory
│       ├── layout.tsx         # Root layout
│       ├── page.tsx           # Home page
│       └── globals.css        # Global styles
├── public/                    # Static assets
├── next.config.ts             # Next.js configuration
├── tsconfig.json              # TypeScript configuration
├── package.json               # Dependencies
├── pnpm-lock.yaml             # Dependency lock file
└── postcss.config.mjs          # PostCSS configuration
```

## Technology Stack

- **Framework**: Next.js 15+
- **Language**: TypeScript
- **Styling**: CSS (with PostCSS)
- **Package Manager**: pnpm
- **Linting**: ESLint

## Development Guidelines

### Code Style
- Follow ESLint configuration
- Use TypeScript for type safety
- Use functional components

### File Naming
- Components: PascalCase (e.g., UserProfile.tsx)
- Utilities: camelCase (e.g., piClient.ts)
- Styles: matching component name (e.g., UserProfile.module.css)

### Environment Variables
- Create .env.local for local development (don't commit)
- Create .env.example for team reference
- Use NEXT_PUBLIC_ prefix for client-side variables

## Debugging

### Browser DevTools
- Open Chrome DevTools (F12)
- Check Console for errors
- Use React DevTools extension for component inspection

### VS Code
- Install "Next.js" extension for better debugging
- Use breakpoints in TypeScript files

## Building for Production

```bash
# Build the application
pnpm build

# Test production build locally
pnpm start
```

## Troubleshooting

### Port Already in Use
```bash
pnpm dev --port 3001
```

### Dependencies Issues
```bash
# Clear pnpm cache
pnpm store prune

# Reinstall dependencies
rm pnpm-lock.yaml
pnpm install
```

### Next.js Cache Issues
```bash
# Clear Next.js cache
rm -rf .next

# Run again
pnpm dev
```

### TypeScript Errors
- Run pnpm type-check to identify issues
- Check tsconfig.json for configuration

## API Integration

Base API URL is configured in .env.local:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Example API call:
```typescript
const response = await fetch(${process.env.NEXT_PUBLIC_API_URL}/api/endpoint/)
```

## Contributing

- Ensure code passes ESLint: pnpm lint
- Run type check before committing: pnpm type-check
- Create meaningful commit messages

## Performance

- Next.js automatically optimizes images
- CSS modules are scoped locally
- Code splitting happens automatically

## License

This project is part of AI Synthetic Workforce
