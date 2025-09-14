// 资产编辑表单组件
import React, { useState, useEffect } from 'react'
import { Asset, AccountType, Currency } from '../types/asset'

interface AssetFormProps {
  asset?: Asset | null
  onSubmit: (asset: Omit<Asset, 'id' | 'timestamp' | 'cnyAmount' | 'assetOrLiability'>) => void
  onCancel: () => void
}

/**
 * 资产编辑表单组件
 * 用于添加或编辑资产信息
 */
const AssetForm: React.FC<AssetFormProps> = ({ asset, onSubmit, onCancel }) => {
  const [accountType, setAccountType] = useState(asset?.accountType || AccountType.PAYMENT)
  const [currency, setCurrency] = useState(asset?.currency || Currency.CNY)
  const [amount, setAmount] = useState(asset?.amount.toString() || '')
  const [description, setDescription] = useState(asset?.description || '')

  // 当asset属性变化时更新表单状态
  useEffect(() => {
    if (asset) {
      setAccountType(asset.accountType)
      setCurrency(asset.currency)
      setAmount(asset.amount.toString())
      setDescription(asset.description)
    }
  }, [asset])

  /**
   * 处理表单提交
   * @param e 表单事件
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // 验证表单数据
    if (!accountType || !currency || !amount || !description) {
      alert('请填写所有必填字段')
      return
    }

    // 转换数据类型
    const assetData = {
      accountType,
      currency,
      amount: parseFloat(amount) || 0,
      description
    }

    // 调用提交回调
    onSubmit(assetData)
  }

  return (
    <div className="asset-form">
      <h2>{asset ? '编辑资产' : '添加资产'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="accountType">账户分类:</label>
          <select
            id="accountType"
            value={accountType}
            onChange={(e) => setAccountType(e.target.value)}
          >
            <option value={AccountType.PAYMENT}>支付账户</option>
            <option value={AccountType.CREDIT_CARD}>信用卡</option>
            <option value={AccountType.OTHER_ASSET}>其他资产</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="currency">币种:</label>
          <select
            id="currency"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
          >
            <option value={Currency.CNY}>人民币 (CNY)</option>
            <option value={Currency.USD}>美元 (USD)</option>
            <option value={Currency.EUR}>欧元 (EUR)</option>
            <option value={Currency.JPY}>日元 (JPY)</option>
            <option value={Currency.HKD}>港币 (HKD)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="amount">金额:</label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            step="0.01"
            placeholder="请输入金额"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">描述:</label>
          <input
            type="text"
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="请输入描述"
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="submit-button">
            {asset ? '更新' : '添加'}
          </button>
          <button type="button" className="cancel-button" onClick={onCancel}>
            取消
          </button>
        </div>
      </form>
    </div>
  )
}

export default AssetForm