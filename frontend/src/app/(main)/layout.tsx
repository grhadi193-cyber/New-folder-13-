import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { getSettings } from '@/lib/api/django'
import ClientTrailWrapper from '@/components/trail/ClientTrailWrapper'

export default async function MainLayout({ children }: { children: React.ReactNode }) {
  let logoUrl: string | null = null
  try {
    const settings = await getSettings()
    logoUrl = settings?.logo ?? null
  } catch {}

  return (
    <ClientTrailWrapper>
      <Navbar logoUrl={logoUrl} />
      <main className="min-h-[calc(100vh-var(--navbar-height))]">
        {children}
      </main>
      <Footer />
    </ClientTrailWrapper>
  )
}
