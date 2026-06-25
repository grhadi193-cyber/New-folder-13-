'use client'
import { createContext, useContext } from 'react'

interface ShopStatus {
  shopEnabled: boolean
  supportPhone: string
  maxOrderQuantity: number
}

const ShopStatusContext = createContext<ShopStatus>({ shopEnabled: true, supportPhone: '', maxOrderQuantity: 20 })

export function ShopStatusProvider({ shopEnabled, supportPhone, maxOrderQuantity, children }: ShopStatus & { children: React.ReactNode }) {
  return (
    <ShopStatusContext.Provider value={{ shopEnabled, supportPhone, maxOrderQuantity }}>
      {children}
    </ShopStatusContext.Provider>
  )
}

export function useShopStatus() {
  return useContext(ShopStatusContext)
}
