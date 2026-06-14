'use client'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname, useRouter } from 'next/navigation'
import { ShoppingCart, User, LogOut, Menu, Settings, Search, X, ChevronDown, Command } from 'lucide-react'
import { useCartStore } from '@/lib/store/cart'
import { useAuthStore } from '@/lib/store/auth'
import { useLoginModal } from '@/lib/store/login-modal'
import { useCartDrawer } from '@/lib/store/cart-drawer'
import MobileMenu from './MobileMenu'
import PulsingDot from '@/components/tracking/PulsingDot'
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

const NAV_LINKS = [
  { href: '/',          label: 'خانه' },
  { href: '/products',  label: 'محصولات', hasMega: true },
  { href: '/software',  label: 'نرم‌افزار' },
  { href: '/blog',      label: 'وبلاگ' },
  { href: '/about',     label: 'درباره ما' },
  { href: '/contact',   label: 'تماس با ما' },
]

const PRODUCT_CATEGORIES = [
  { href: '/products?cat=vehicle', label: 'ردیاب خودرو', desc: 'خودروهای شخصی و سازمانی' },
  { href: '/products?cat=fleet', label: 'ردیاب ناوگان', desc: 'مدیریت ناوگان تجاری' },
  { href: '/products?cat=personal', label: 'ردیاب شخصی', desc: 'افراد و کودکان' },
  { href: '/products?cat=motorcycle', label: 'ردیاب موتور', desc: 'موتورسیکلت و دوچرخه' },
  { href: '/products', label: 'همه محصولات', desc: 'مشاهده کلیه محصولات' },
]

interface NavbarProps {
  logoUrl?: string | null
}

export default function Navbar({ logoUrl }: NavbarProps = {}) {
  const pathname = usePathname()
  const router = useRouter()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [megaOpen, setMegaOpen] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)
  const megaRef = useRef<HTMLDivElement>(null)
  const totalCount = useCartStore((s) => s.totalCount())
  const { user, token, logout } = useAuthStore()
  const openLogin = useLoginModal((s) => s.openLogin)
  const openCartDrawer = useCartDrawer((s) => s.openDrawer)

  const displayName = user?.full_name || user?.phone_number || ''

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (searchOpen && searchRef.current) searchRef.current.focus()
  }, [searchOpen])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (megaRef.current && !megaRef.current.contains(e.target as Node)) {
        setMegaOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/products?q=${encodeURIComponent(searchQuery.trim())}`)
      setSearchOpen(false)
      setSearchQuery('')
    }
  }

  return (
    <>
      <header
        className={cn(
          'sticky top-0 z-[300] transition-all duration-300',
          scrolled
            ? 'bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-sm'
            : 'bg-white'
        )}
      >
        <div className="absolute top-0 inset-x-0 h-[2px] bg-teal-500" />

        <div className="container mx-auto px-4 h-[var(--navbar-height)] flex items-center justify-between gap-4">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 shrink-0 group/logo">
            {logoUrl ? (
              <div className="relative w-10 h-10 rounded-xl overflow-hidden shadow-md group-hover/logo:shadow-lg group-hover/logo:scale-105 transition-all duration-300">
                <Image
                  src={logoUrl}
                  alt="آتی فرزام ایرانیان"
                  fill
                  className="object-contain"
                />
              </div>
            ) : (
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-navy-deeper to-navy flex items-center justify-center shadow-md group-hover/logo:shadow-lg group-hover/logo:scale-105 transition-all duration-300">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-white">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="currentColor"/>
                </svg>
              </div>
            )}
            <div className="hidden sm:block">
              <p className="text-sm font-bold text-navy leading-tight">آتی فرزام</p>
              <div className="flex items-center gap-1.5">
                <PulsingDot color="green" size={6} />
                <p className="text-[10px] text-text-tertiary leading-tight">آنلاین</p>
              </div>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center gap-0.5">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href))
              return (
                <div
                  key={link.href}
                  className="relative"
                  ref={link.hasMega ? megaRef : undefined}
                  onMouseEnter={() => link.hasMega && setMegaOpen(true)}
                  onMouseLeave={() => link.hasMega && setMegaOpen(false)}
                >
                  <Link
                    href={link.href}
                    className={cn(
                      'flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-all duration-200',
                      isActive
                        ? 'text-navy font-medium bg-slate-100'
                        : 'text-slate-500 hover:text-navy hover:bg-slate-50'
                    )}
                  >
                    {link.label}
                    {link.hasMega && (
                      <ChevronDown className={cn(
                        'w-3.5 h-3.5 transition-transform duration-300',
                        megaOpen && 'rotate-180'
                      )} />
                    )}

                  </Link>

                  {link.hasMega && megaOpen && (
                    <div className="absolute top-full right-0 mt-1 w-72 animate-fade-in">
                      <div className="bg-white border border-slate-100 shadow-xl rounded-2xl p-3">
                        <div className="space-y-0.5">
                          {PRODUCT_CATEGORIES.map((cat) => (
                            <Link
                              key={cat.href}
                              href={cat.href}
                              className="flex flex-col gap-0.5 px-4 py-3 rounded-xl hover:bg-slate-50 transition-all duration-200 group/cat"
                            >
                              <span className="text-sm font-medium text-slate-700 group-hover/cat:text-navy transition-colors">
                                {cat.label}
                              </span>
                              <span className="text-[11px] text-slate-400">
                                {cat.desc}
                              </span>
                            </Link>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-1.5">

            {/* Search */}
            <div className="relative">
              <button
                onClick={() => setSearchOpen(!searchOpen)}
                className={cn(
                  'p-2 rounded-lg transition-all duration-200',
                  searchOpen
                    ? 'bg-slate-100 text-navy'
                    : 'text-slate-400 hover:text-navy hover:bg-slate-50'
                )}
                aria-label="جستجو"
              >
                <Search className="w-[18px] h-[18px]" />
              </button>
              {!searchOpen && (
                <div className="hidden lg:flex absolute -bottom-1 -left-1 items-center gap-0.5 px-1 py-0.5 bg-bg-secondary rounded text-[8px] text-text-tertiary font-mono border border-border-default/30 pointer-events-none">
                  <Command className="w-2 h-2" />K
                </div>
              )}

              {searchOpen && (
                <div className="absolute top-full left-0 mt-2 w-80 animate-fade-in z-50">
                  <form onSubmit={handleSearch} className="bg-white rounded-xl shadow-xl p-3 border border-slate-100">
                    <div className="relative">
                      <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <input
                        ref={searchRef}
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="جستجوی محصولات..."
                        className="w-full pr-10 pl-10 py-2.5 rounded-lg bg-slate-50 border border-slate-200 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-teal-400 focus:ring-2 focus:ring-teal-100 transition-all"
                      />
                      <button
                        type="button"
                        onClick={() => { setSearchOpen(false); setSearchQuery('') }}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </form>
                </div>
              )}
            </div>

            {/* Cart */}
            <button
              onClick={openCartDrawer}
              className="relative p-2 rounded-lg transition-all duration-200 text-slate-400 hover:text-navy hover:bg-slate-50"
              aria-label="سبد خرید"
            >
              <ShoppingCart className="w-[18px] h-[18px]" />
              <AnimatePresence>
                {totalCount > 0 && (
                  <motion.span
                    key={totalCount}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 15 }}
                    className="absolute -top-1 -right-1 w-4 h-4 bg-teal-500 text-white text-[10px] rounded-full flex items-center justify-center"
                  >
                    {totalCount > 99 ? '99+' : totalCount.toLocaleString('fa-IR')}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>

            {/* Auth */}
            {token && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-50 transition-all duration-200 text-slate-500 hover:text-navy">
                    <div className="w-7 h-7 rounded-full bg-navy flex items-center justify-center">
                      <User className="w-3.5 h-3.5 text-white" />
                    </div>
                    <span className="hidden sm:block text-sm font-medium max-w-[100px] truncate">
                      {displayName}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-52 rounded-xl p-1.5 animate-scale-in">
                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer">
                      <User className="w-4 h-4 text-text-tertiary" />
                      پروفایل
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/profile/orders" className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer">
                      <Settings className="w-4 h-4 text-text-tertiary" />
                      سفارش‌ها
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="my-1" />
                  <DropdownMenuItem
                    onClick={logout}
                    className="text-error focus:text-error flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                    خروج
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <button
                onClick={() => openLogin()}
                className="flex items-center gap-2 px-4 py-2 bg-navy text-white rounded-lg text-sm font-medium hover:bg-navy-dark transition-colors shadow-sm hover:shadow-navy"
              >
                <User className="w-4 h-4" />
                <span className="hidden sm:block">ورود</span>
              </button>
            )}

            {/* Mobile menu toggle */}
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-slate-50 transition-all duration-200 text-slate-400"
              onClick={() => setMobileOpen(true)}
              aria-label="منو"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <MobileMenu open={mobileOpen} onClose={() => setMobileOpen(false)} />
    </>
  )
}
