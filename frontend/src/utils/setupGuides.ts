import type { Language } from '@/types';

export interface SetupGuide {
  language: string;
  dependencies: string[];
  packageManager: string;
  installCommand: string;
  runCommand: string;
  configFiles: { name: string; content: string }[];
  notes: string[];
}

export const SETUP_GUIDES: Record<Language, SetupGuide> = {
  python: {
    language: 'Python',
    dependencies: ['Python 3.8+'],
    packageManager: 'pip',
    installCommand: 'pip install -r requirements.txt',
    runCommand: 'python main.py',
    configFiles: [
      {
        name: 'requirements.txt',
        content: '# Add your dependencies here\n# Example:\n# requests==2.31.0\n# flask==3.0.0'
      }
    ],
    notes: [
      'Create a virtual environment: python -m venv venv',
      'Activate it: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)',
      'Install dependencies with pip'
    ]
  },

  nodejs: {
    language: 'Node.js',
    dependencies: ['Node.js 18+', 'npm or yarn'],
    packageManager: 'npm',
    installCommand: 'npm install',
    runCommand: 'node index.js',
    configFiles: [
      {
        name: 'package.json',
        content: `{
  "name": "my-project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {}
}`
      }
    ],
    notes: [
      'Initialize project: npm init -y',
      'Install packages: npm install <package-name>',
      'Run with: npm start'
    ]
  },

  javascript: {
    language: 'JavaScript',
    dependencies: ['Modern web browser or Node.js'],
    packageManager: 'npm',
    installCommand: 'npm install',
    runCommand: 'Open in browser or node script.js',
    configFiles: [
      {
        name: 'index.html',
        content: `<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
</head>
<body>
    <script src="script.js"></script>
</body>
</html>`
      }
    ],
    notes: [
      'For browser: Include in HTML with <script> tag',
      'For Node.js: Run with node command',
      'Use ES6 modules with type="module"'
    ]
  },

  typescript: {
    language: 'TypeScript',
    dependencies: ['Node.js 18+', 'TypeScript'],
    packageManager: 'npm',
    installCommand: 'npm install && npm install -D typescript @types/node',
    runCommand: 'npm run build && node dist/index.js',
    configFiles: [
      {
        name: 'tsconfig.json',
        content: `{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  }
}`
      },
      {
        name: 'package.json',
        content: `{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}`
      }
    ],
    notes: [
      'Install TypeScript: npm install -D typescript',
      'Compile: npx tsc or npm run build',
      'Use ts-node for development: npm install -D ts-node'
    ]
  },

  java: {
    language: 'Java',
    dependencies: ['JDK 11+', 'Maven or Gradle'],
    packageManager: 'Maven',
    installCommand: 'mvn install',
    runCommand: 'java -cp target/classes Main',
    configFiles: [
      {
        name: 'pom.xml',
        content: `<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0</version>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
</project>`
      }
    ],
    notes: [
      'Compile: javac Main.java',
      'Run: java Main',
      'Use Maven/Gradle for dependency management'
    ]
  },

  php: {
    language: 'PHP',
    dependencies: ['PHP 8.0+', 'Composer'],
    packageManager: 'Composer',
    installCommand: 'composer install',
    runCommand: 'php index.php',
    configFiles: [
      {
        name: 'composer.json',
        content: `{
    "name": "my-project",
    "require": {
        "php": ">=8.0"
    },
    "autoload": {
        "psr-4": {
            "App\\\\": "src/"
        }
    }
}`
      }
    ],
    notes: [
      'Install Composer from getcomposer.org',
      'Add dependencies: composer require <package>',
      'Run built-in server: php -S localhost:8000'
    ]
  },

  golang: {
    language: 'Go',
    dependencies: ['Go 1.20+'],
    packageManager: 'go mod',
    installCommand: 'go mod download',
    runCommand: 'go run main.go',
    configFiles: [
      {
        name: 'go.mod',
        content: `module myproject

go 1.20

require (
    // Add dependencies here
)`
      }
    ],
    notes: [
      'Initialize module: go mod init myproject',
      'Add dependency: go get <package>',
      'Build: go build',
      'Run: go run main.go'
    ]
  },

  c: {
    language: 'C',
    dependencies: ['GCC or Clang compiler'],
    packageManager: 'Manual',
    installCommand: 'N/A',
    runCommand: './program',
    configFiles: [
      {
        name: 'Makefile',
        content: `CC=gcc
CFLAGS=-Wall -Wextra -std=c11

program: main.c
\t$(CC) $(CFLAGS) -o program main.c

clean:
\trm -f program`
      }
    ],
    notes: [
      'Compile: gcc -o program main.c',
      'Run: ./program',
      'Use Make for complex projects'
    ]
  },

  cpp: {
    language: 'C++',
    dependencies: ['G++ or Clang++ compiler'],
    packageManager: 'CMake',
    installCommand: 'cmake . && make',
    runCommand: './program',
    configFiles: [
      {
        name: 'CMakeLists.txt',
        content: `cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)

add_executable(program main.cpp)`
      }
    ],
    notes: [
      'Compile: g++ -o program main.cpp',
      'Run: ./program',
      'Use CMake for larger projects'
    ]
  },

  csharp: {
    language: 'C#',
    dependencies: ['.NET SDK 6.0+'],
    packageManager: 'NuGet',
    installCommand: 'dotnet restore',
    runCommand: 'dotnet run',
    configFiles: [
      {
        name: 'Program.csproj',
        content: `<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>`
      }
    ],
    notes: [
      'Create project: dotnet new console',
      'Add package: dotnet add package <PackageName>',
      'Build: dotnet build',
      'Run: dotnet run'
    ]
  },

  rust: {
    language: 'Rust',
    dependencies: ['Rust 1.70+', 'Cargo'],
    packageManager: 'Cargo',
    installCommand: 'cargo build',
    runCommand: 'cargo run',
    configFiles: [
      {
        name: 'Cargo.toml',
        content: `[package]
name = "my_project"
version = "0.1.0"
edition = "2021"

[dependencies]
# Add dependencies here`
      }
    ],
    notes: [
      'Create project: cargo new my_project',
      'Add dependency in Cargo.toml',
      'Build: cargo build',
      'Run: cargo run'
    ]
  },

  sql: {
    language: 'SQL',
    dependencies: ['Database (PostgreSQL, MySQL, SQLite, etc.)'],
    packageManager: 'Database-specific',
    installCommand: 'Install database server',
    runCommand: 'Execute via database client',
    configFiles: [
      {
        name: 'schema.sql',
        content: `-- Database schema
-- Run with: psql -d database -f schema.sql

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);`
      }
    ],
    notes: [
      'PostgreSQL: psql -d database -f script.sql',
      'MySQL: mysql -u user -p database < script.sql',
      'SQLite: sqlite3 database.db < script.sql'
    ]
  },

  drizzle: {
    language: 'Drizzle ORM',
    dependencies: ['Node.js 18+', 'Drizzle ORM', 'Drizzle Kit'],
    packageManager: 'npm',
    installCommand: 'npm install drizzle-orm && npm install -D drizzle-kit',
    runCommand: 'npx drizzle-kit generate:pg',
    configFiles: [
      {
        name: 'drizzle.config.ts',
        content: `import type { Config } from 'drizzle-kit';

export default {
  schema: './src/schema.ts',
  out: './drizzle',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
} satisfies Config;`
      },
      {
        name: 'schema.ts',
        content: `import { pgTable, serial, text, varchar } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
});`
      }
    ],
    notes: [
      'Install: npm install drizzle-orm',
      'Install dev tools: npm install -D drizzle-kit',
      'Generate migrations: npx drizzle-kit generate:pg',
      'Push to database: npx drizzle-kit push:pg'
    ]
  },

  prisma: {
    language: 'Prisma',
    dependencies: ['Node.js 18+', 'Prisma CLI'],
    packageManager: 'npm',
    installCommand: 'npm install && npx prisma generate',
    runCommand: 'npx prisma migrate dev',
    configFiles: [
      {
        name: '.env',
        content: `DATABASE_URL="postgresql://user:password@localhost:5432/mydb"`
      }
    ],
    notes: [
      'Install: npm install prisma @prisma/client',
      'Initialize: npx prisma init',
      'Generate client: npx prisma generate',
      'Run migrations: npx prisma migrate dev'
    ]
  },
};
