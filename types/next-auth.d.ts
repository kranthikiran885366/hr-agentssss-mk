import NextAuth, { DefaultSession } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      role: 'ADMIN' | 'MANAGER' | 'USER';
    } & DefaultSession['user'];
  }

  interface User {
    role: 'ADMIN' | 'MANAGER' | 'USER';
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role?: 'ADMIN' | 'MANAGER' | 'USER';
  }
}
