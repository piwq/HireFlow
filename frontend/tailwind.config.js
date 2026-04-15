/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          dark: {
            base: '#0D0F1A',
            surface: '#151827',
            elevated: '#1E2235',
            border: '#2A2F4A',
            primary: '#E2E8F0',
            secondary: '#94A3B8',
            muted: '#4B5563',
          },
          light: {
            base: '#F8FAFC',
            surface: '#FFFFFF',
            elevated: '#F1F5F9',
            border: '#E2E8F0',
            primary: '#0F172A',
            secondary: '#475569',
            muted: '#94A3B8',
          },
          accent: {
            DEFAULT: '#6366F1',
            hover: '#4F46E5',
          },
          status: {
            new: '#3B82F6',
            screening: '#F59E0B',
            interview: '#8B5CF6',
            hired: '#10B981',
            rejected: '#EF4444',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display': ['24px', { lineHeight: '32px', fontWeight: '700' }],
        'heading': ['18px', { lineHeight: '28px', fontWeight: '600' }],
        'body': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'label': ['13px', { lineHeight: '18px', fontWeight: '500' }],
        'caption': ['12px', { lineHeight: '16px', fontWeight: '400' }],
        'micro': ['11px', { lineHeight: '14px', fontWeight: '500' }],
      }
    },
  },
  plugins: [],
}

