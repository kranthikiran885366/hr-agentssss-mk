import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { prisma } from './db';
import { compare } from 'bcryptjs';

export const authOptions = {
  // Configure one or more authentication providers
  adapter: PrismaAdapter(prisma),
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Please enter your email and password');
        }

        // Find user by email
        const user = await prisma.user.findUnique({
          where: { email: credentials.email },
          select: {
            id: true,
            name: true,
            email: true,
            password: true,
            role: true,
            department: true,
            image: true
          }
        });

        if (!user || !user.password) {
          throw new Error('Invalid email or password');
        }

        // Verify password
        const isValid = await compare(credentials.password, user.password);
        if (!isValid) {
          throw new Error('Invalid email or password');
        }

        // Return user object without password
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { password, ...userWithoutPassword } = user;
        return userWithoutPassword;
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }: { token: any; user: any }) {
      // Initial sign in
      if (user) {
        token.role = user.role;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }: { session: any; token: any }) {
      if (session?.user) {
        session.user.role = token.role;
        session.user.id = token.id;
      }
      return session;
    },
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === 'development',
} as const;

// Helper function to get server session
export async function getServerSession() {
  return await import('next-auth').then((mod) => 
    mod.getServerSession(authOptions)
  );
}

// Helper function to protect API routes
export function withAuth(handler: any) {
  return async (req: any, res: any) => {
    const session = await getServerSession();
    if (!session) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    return handler(req, res, session.user);
  };
}

// Helper function to check user role
export function withRole(roles: string[]) {
  return async (req: any, res: any, next: any) => {
    const session = await getServerSession();
    if (!session) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    if (!roles.includes(session.user.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    return next();
  };
}
