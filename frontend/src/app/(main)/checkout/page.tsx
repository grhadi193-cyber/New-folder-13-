'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ShoppingCart, LogIn, User, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import StepIndicator from '@/components/checkout/StepIndicator'
import AddressStep from '@/components/checkout/AddressStep'
import ShippingStep from '@/components/checkout/ShippingStep'
import ConfirmStep from '@/components/checkout/ConfirmStep'
import { useAuthStore } from '@/lib/store/auth'
import { useCartStore } from '@/lib/store/cart'
import { useLoginModal } from '@/lib/store/login-modal'
import { updateProfile } from '@/lib/api/django'
import BreadcrumbTrail from '@/components/trail/BreadcrumbTrail'
import { SignalStrength } from '@/components/tracking'
import { motion } from 'framer-motion'
import { toast } from 'sonner'

export default function CheckoutPage() {
  const { token, user } = useAuthStore()
  const updateUser = useAuthStore((s) => s.updateUser)
  const { items } = useCartStore()
  const openLogin = useLoginModal((s) => s.openLogin)

  const profileName = user?.full_name?.trim() || ''
  const [customerName, setCustomerName] = useState(profileName)
  const [nameConfirmed, setNameConfirmed] = useState(!!profileName)
  const [savingName, setSavingName] = useState(false)
  const [step, setStep] = useState(1)
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)
  const [selectedAddress, setSelectedAddress] = useState<any>(null)
  const [selectedShippingMethod, setSelectedShippingMethod] = useState<any>(null)

  const handleNameConfirm = async () => {
    if (!customerName.trim()) return
    setNameConfirmed(true)
    if (token && customerName.trim() !== profileName) {
      setSavingName(true)
      try {
        await updateProfile(token, { full_name: customerName.trim() })
        updateUser({ full_name: customerName.trim() })
      } catch {
        // silent — name still works for this order
      } finally {
        setSavingName(false)
      }
    }
  }

  useEffect(() => {
    if (!token) {
      openLogin({
        message: 'برای تکمیل سفارش وارد شوید',
        returnUrl: '/checkout',
      })
    }
  }, [token, openLogin])

  if (!token) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center" dir="rtl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-sm mx-auto px-4"
        >
          <div className="w-20 h-20 rounded-2xl bg-[#1e3a5f]/10 flex items-center justify-center mx-auto mb-6">
            <LogIn className="w-10 h-10 text-[#1e3a5f]" />
          </div>
          <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">ورود به حساب</h2>
          <p className="text-gray-400 text-sm mb-6">
            برای تکمیل سفارش ابتدا وارد حساب کاربری خود شوید. پنل ورود باز شده است.
          </p>
          <Button
            onClick={() => openLogin({ message: 'برای تکمیل سفارش وارد شوید', returnUrl: '/checkout' })}
            className="bg-gradient-to-l from-[#1e3a5f] to-[#2a4f7a] text-white rounded-xl font-bold px-8 shadow-lg hover:scale-[1.02] transition-transform"
          >
            <LogIn className="w-4 h-4 ml-2" />
            ورود به حساب
          </Button>
        </motion.div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center" dir="rtl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-sm mx-auto px-4"
        >
          <div className="w-20 h-20 rounded-2xl bg-[#f59e0b]/10 flex items-center justify-center mx-auto mb-6">
            <ShoppingCart className="w-10 h-10 text-[#f59e0b]" />
          </div>
          <h2 className="text-xl font-bold text-[#1e3a5f] mb-2">سبد خرید خالی است</h2>
          <p className="text-gray-400 text-sm mb-6">
            ابتدا محصولات مورد نظر خود را به سبد اضافه کنید.
          </p>
          <Button
            asChild
            className="bg-gradient-to-l from-[#1e3a5f] to-[#2a4f7a] text-white rounded-xl font-bold px-8 shadow-lg hover:scale-[1.02] transition-transform"
          >
            <Link href="/products">مشاهده محصولات</Link>
          </Button>
        </motion.div>
      </div>
    )
  }

  const handleAddressSelect = (id: number, addressObj?: any) => {
    setSelectedAddressId(id)
    if (addressObj) setSelectedAddress(addressObj)
  }

  const handleAddressNext = () => {
    setStep(2)
  }

  return (
    <div className="min-h-screen bg-white" dir="rtl">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-6 flex items-center gap-3">
          <BreadcrumbTrail dark={false} />
        </div>

        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-[#1e3a5f]">تکمیل سفارش</h1>
          <div className="flex items-center gap-2">
            <SignalStrength bars={step === 1 ? 1 : step === 2 ? 2 : 3} activeColor="#10b981" />
            <span className="text-xs text-gray-400">مرحله {step} از ۳</span>
          </div>
        </div>

        <div className="mb-10">
          <StepIndicator currentStep={step} />
        </div>

        {/* نام مشتری */}
        {nameConfirmed ? (
          <div className="mb-6 flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#10b981]/10 flex items-center justify-center">
                <User className="w-4 h-4 text-[#10b981]" />
              </div>
              <div>
                <p className="text-xs text-gray-400">سفارش‌دهنده</p>
                <p className="text-sm font-semibold text-[#1e3a5f]">{customerName}</p>
              </div>
            </div>
            <button
              onClick={() => setNameConfirmed(false)}
              className="text-xs text-gray-400 hover:text-[#1e3a5f] transition-colors px-3 py-1.5 rounded-lg hover:bg-white"
            >
              ویرایش
            </button>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-5 rounded-2xl border border-amber-200 bg-amber-50/50"
          >
            <div className="flex items-center gap-2 mb-3">
              <User className="w-5 h-5 text-amber-600" />
              <p className="font-bold text-amber-800 text-sm">نام و نام خانوادگی</p>
            </div>
            <p className="text-xs text-amber-700 mb-3">
              لطفاً نام کامل خود را وارد کنید. این نام روی فاکتور سفارش ثبت می‌شود.
            </p>
            <div className="flex gap-3">
              <div className="flex-1">
                <Label className="sr-only">نام و نام خانوادگی</Label>
                <Input
                  placeholder="نام و نام خانوادگی"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="h-11 rounded-xl"
                  dir="rtl"
                  onKeyDown={(e) => { if (e.key === 'Enter' && customerName.trim()) handleNameConfirm() }}
                />
              </div>
              <Button
                className="h-11 px-6 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-semibold"
                onClick={handleNameConfirm}
                disabled={!customerName.trim() || savingName}
              >
                {savingName ? (
                  <span className="flex items-center gap-1.5">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ذخیره...
                  </span>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4 ml-1.5" />
                    تأیید
                  </>
                )}
              </Button>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {!nameConfirmed ? (
              <div className="text-center py-12 text-gray-400">
                <User className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p className="text-sm">لطفاً ابتدا نام خود را تأیید کنید</p>
              </div>
            ) : (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              {step === 1 && (
                <AddressStep
                  token={token}
                  selectedId={selectedAddressId}
                  onSelect={handleAddressSelect}
                  onNext={handleAddressNext}
                />
              )}

              {step === 2 && selectedAddressId && (
                <ShippingStep
                  addressId={selectedAddressId}
                  address={selectedAddress}
                  selectedMethodId={selectedShippingMethod?.id ?? null}
                  onSelect={(method) => setSelectedShippingMethod(method)}
                  onNext={() => setStep(3)}
                  onBack={() => setStep(1)}
                />
              )}

              {step === 3 && selectedShippingMethod && (
                <ConfirmStep
                  token={token}
                  address={selectedAddress ?? { id: selectedAddressId }}
                  shippingMethod={selectedShippingMethod}
                  customerName={customerName}
                  onBack={() => setStep(2)}
                />
              )}
            </motion.div>
            )}
          </div>

          <div className="lg:col-span-1">
            <div className="sticky top-24 rounded-2xl shadow-md bg-[#f1f5f9] p-5 space-y-4">
              <h3 className="font-bold text-[#1e3a5f] text-sm">خلاصه سفارش</h3>
              <div className="space-y-2">
                {items.map((item) => (
                  <div key={item.product_id} className="flex justify-between text-xs">
                    <span className="text-gray-500 truncate ml-2">{item.name} x{item.quantity}</span>
                    <span className="text-[#1e3a5f] font-semibold whitespace-nowrap">
                      {new Intl.NumberFormat('fa-IR').format(item.price * item.quantity)} تومان
                    </span>
                  </div>
                ))}
              </div>
              {selectedShippingMethod && (
                <>
                  <div className="h-px bg-gray-200" />
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">هزینه ارسال</span>
                    <span className="text-[#10b981] font-semibold">
                      {selectedShippingMethod.cost === 0
                        ? 'رایگان'
                        : `${new Intl.NumberFormat('fa-IR').format(selectedShippingMethod.cost)} تومان`}
                    </span>
                  </div>
                </>
              )}
              <div className="h-px bg-gray-200" />
              <div className="flex justify-between text-sm font-bold">
                <span className="text-[#1e3a5f]">جمع کل</span>
                <span className="text-[#1e3a5f]">
                  {new Intl.NumberFormat('fa-IR').format(
                    items.reduce((s, i) => s + i.price * i.quantity, 0) + (selectedShippingMethod?.cost ?? 0)
                  )} تومان
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
