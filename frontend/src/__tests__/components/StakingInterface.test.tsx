import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import StakingInterface from '@/components/StakingInterface'
import * as enhancements from '@/lib/api/enhancements'

let stakeMock: jest.SpyInstance
let getPositionsMock: jest.SpyInstance
let getTierStatsMock: jest.SpyInstance
let getPlatformRevenueMock: jest.SpyInstance
let claimRewardsMock: jest.SpyInstance
let unstakeMock: jest.SpyInstance
let alertSpy: jest.SpyInstance
let confirmSpy: jest.SpyInstance

jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => ({
    connected: true,
    publicKey: { toBase58: () => 'DevnetWallet1111111111111111111111111111' },
  }),
}))

describe('StakingInterface (devnet fallback)', () => {
  beforeEach(() => {
    stakeMock = jest.spyOn(enhancements.tokenAPI, 'stake').mockResolvedValue({ success: true })
    getPositionsMock = jest
      .spyOn(enhancements.tokenAPI, 'getStakingPositions')
      .mockResolvedValue({ positions: [] })
    getTierStatsMock = jest.spyOn(enhancements.tokenAPI, 'getTierStats').mockResolvedValue({ tiers: {} })
    getPlatformRevenueMock = jest
      .spyOn(enhancements.tokenAPI, 'getPlatformRevenue')
      .mockResolvedValue({})
    claimRewardsMock = jest
      .spyOn(enhancements.tokenAPI, 'claimRewards')
      .mockResolvedValue({ success: true, amount_claimed: 0 })
    unstakeMock = jest
      .spyOn(enhancements.tokenAPI, 'unstake')
      .mockResolvedValue({ success: true, amount_returned: 0 })

    window.history.pushState({}, '', '?payment_method=false')
    alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})
    confirmSpy = jest.spyOn(window, 'confirm').mockImplementation(() => true)
  })

  afterEach(() => {
    jest.useRealTimers()
    alertSpy.mockRestore()
    confirmSpy.mockRestore()
    stakeMock.mockRestore()
    getPositionsMock.mockRestore()
    getTierStatsMock.mockRestore()
    getPlatformRevenueMock.mockRestore()
    claimRewardsMock.mockRestore()
    unstakeMock.mockRestore()
  })

  it('simulates staking on devnet when payment_method=false is present', async () => {
    jest.useFakeTimers()

    render(
      <StakingInterface userId={42} walletAddress="DevnetWallet1111111111111111111111111111" currentBalance={500_000} />
    )

    const amountInput = screen.getByPlaceholderText('Enter amount') as HTMLInputElement
    fireEvent.change(amountInput, { target: { value: '1000' } })

    const stakeButton = screen.getByRole('button', { name: /stake for/i })
    fireEvent.click(stakeButton)

    await act(async () => {
      jest.advanceTimersByTime(1600)
    })

    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('Devnet Mode'))
    })

    expect(stakeMock).not.toHaveBeenCalled()
  })
})


