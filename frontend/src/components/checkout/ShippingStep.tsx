'use client'
import { useEffect, useState } from 'react'
import { Check, Truck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatPrice } from '@/lib/utils'
import { calculateShipping } from '@/lib/api/django'
import { useCartStore } from '@/lib/store/cart'

interface ShippingMethod {
  id: number
  name: string
  description?: string
  delivery_days: number
  price: number
}

interface ShippingStepProps {
  addressId: number
  selectedMethodId: number | null
  onSelect: (method: ShippingMethod) => void
  onNext: () => void
  onBack: () => void
}

export default function ShippingStep({
  addressId, selectedMethodId, onSelect, onNext, onBack
}: ShippingStepProps) {
  const [methods, setMethods] = useState<ShippingMethod[]>([])
  const [loading, setLoading] = useState(true)
  const { items } = useCartStore()

  useEffect(() => {
    const load = async () => {
      try {
        const data = await calculateShipping({
          address_id: addressId,
          items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
        })
        setMethods(Array.isArray(data) ? data : data.methods ?? [])
      } catch {
        // fallback mock for UI
        setMethods([
          { id: 1, name: 'پست عادی', description: 'ارسال از طریق پست', delivery_days: 7, price: 35000 },
          { id: 2, name: 'پست پیشتاز', description: 'ارسال سریع', delivery_days: 3, price: 65000 },
          { id: 3, name: 'پیک موتوری', description: 'ارسال همان روز (تهران)', delivery_days: 1, price: 95000 },
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [addressId])

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full rounded-xl" />)}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-text-primary mb-4">انتخاب روش ارسال</h2>

      {methods.map((method) => (
        <Card
          key={method.id}
          onClick={() => onSelect(method)}
          className={cn(
            'cursor-pointer transition-all border-2',
            selectedMethodId === method.id
              ? 'border-navy bg-navy/5 shadow-[var(--shadow-navy)]'
              : 'border-border-default hover:border-navy/40'
          )}
        >
          <CardContent className="p-4 flex items-center gap-4">
            <div
              className={cn(
                'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0',
                selectedMethodId === method.id ? 'border-navy bg-navy' : 'border-border-default'
              )}
            >
              {selectedMethodId === method.id && <Check className="w-3 h-3 text-white" />}
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Truck className="w-4 h-4 text-teal flex-shrink-0" />
                <p className="font-semibold text-text-primary text-sm">{method.name}</p>
              </div>
              {method.description && (
                <p className="text-text-secondary text-xs mt-0.5">{method.description}</p>
              )}
              <p className="text-text-tertiary text-xs mt-1">
                زمان تحویل: {method.delivery_days === 1 ? 'همان روز' : `${method.delivery_days} روز کاری`}
              </p>
            </div>

            <div className="text-left flex-shrink-0">
              <p className="font-bold text-navy text-sm">{formatPrice(method.price)}</p>
            </div>
          </CardContent>
        </Card>
      ))}

      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={onBack}>
          مرحله قبل
        </Button>
        <Button
          className="bg-navy hover:bg-navy-dark text-white px-8"
          onClick={onNext}
          disabled={!selectedMethodId}
        >
          مرحله بعد
        </Button>
      </div>
    </div>
  )
}
