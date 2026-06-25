import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'
import { getSettings, djangoImageUrl } from '@/lib/api/django'
import ClientTrailWrapper from '@/components/trail/ClientTrailWrapper'
import { ShopStatusProvider } from '@/lib/store/shop-status'

export const dynamic = 'force-dynamic'

export default async function MainLayout({ children }: { children: React.ReactNode }) {
  let logoUrl: string | null = null
  let shopEnabled = true
  let supportPhone = ''
  let maxOrderQuantity = 20
  try {
    const settings = await getSettings()
    logoUrl = settings?.logo ? djangoImageUrl(settings.logo) : null
    shopEnabled = settings?.shop_enabled !== false
    supportPhone = settings?.support_phone ?? ''
    maxOrderQuantity = settings?.max_order_quantity ?? 20
  } catch {}

  return (
    <ShopStatusProvider shopEnabled={shopEnabled} supportPhone={supportPhone} maxOrderQuantity={maxOrderQuantity}>
      <ClientTrailWrapper>
        <Navbar logoUrl={logoUrl} />
        <main className="min-h-[calc(100vh-var(--navbar-height))]">
          {children}
        </main>
        <Footer />
      </ClientTrailWrapper>
    </ShopStatusProvider>
  )
}
