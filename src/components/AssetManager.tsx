// 资产管理主组件
import React, { useState, useEffect } from 'react'
import { Asset } from '../types/asset'
import assetService from '../services/assetService'
import AssetList from './AssetList'

/**
 * 资产管理主组件
 * 负责加载资产数据并管理整个资产管理界面的状态
 */
const AssetManager: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 组件挂载时加载资产数据
  useEffect(() => {
    loadAssets()
  }, [])

  /**
   * 加载资产数据
   */
  const loadAssets = async () => {
    try {
      setLoading(true)
      const data = await assetService.loadAssets()
      setAssets(data)
      setError(null)
    } catch (err) {
      setError('加载资产数据失败')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  /**
   * 处理资产数据变化
   * @param newAssets 新的资产数据
   */
  const handleAssetsChange = (newAssets: Asset[]) => {
    setAssets(newAssets)
  }

  // 渲染加载状态
  if (loading) {
    return <div className="loading">加载中...</div>
  }

  // 渲染错误状态
  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <div className="asset-manager">
      <AssetList 
        assets={assets} 
        onAssetsChange={handleAssetsChange} 
      />
    </div>
  )
}

export default AssetManager