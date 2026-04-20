/**
 * ML Model Drift Monitor
 * Tracks detection confidence over time to detect model degradation
 */

interface DetectionMetric {
  timestamp: number
  model: string
  confidence: number
  detectionCount: number
  processingTimeMs: number
}

interface DriftReport {
  model: string
  period: string
  avgConfidence: number
  avgProcessingTime: number
  detectionRate: number
  trend: 'stable' | 'degrading' | 'improving' | 'insufficient_data'
  sampleCount: number
}

class DriftMonitor {
  private metrics: DetectionMetric[] = []
  private maxMetrics = 5000
  private windowMs = 5 * 60 * 1000 // 5 minutes

  record(model: string, confidence: number, detectionCount: number, processingTimeMs: number) {
    this.metrics.push({
      timestamp: Date.now(),
      model,
      confidence,
      detectionCount,
      processingTimeMs,
    })

    // Prune old metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-Math.floor(this.maxMetrics * 0.8))
    }
  }

  getReport(model: string): DriftReport {
    const now = Date.now()
    const recentMetrics = this.metrics.filter(
      m => m.model === model && now - m.timestamp < this.windowMs
    )

    if (recentMetrics.length < 10) {
      return {
        model,
        period: '5min',
        avgConfidence: 0,
        avgProcessingTime: 0,
        detectionRate: 0,
        trend: 'insufficient_data',
        sampleCount: recentMetrics.length,
      }
    }

    const avgConfidence = recentMetrics.reduce((sum, m) => sum + m.confidence, 0) / recentMetrics.length
    const avgProcessingTime = recentMetrics.reduce((sum, m) => sum + m.processingTimeMs, 0) / recentMetrics.length
    const detectionRate = recentMetrics.filter(m => m.detectionCount > 0).length / recentMetrics.length

    // Compare first half vs second half for trend
    const mid = Math.floor(recentMetrics.length / 2)
    const firstHalf = recentMetrics.slice(0, mid)
    const secondHalf = recentMetrics.slice(mid)

    const firstAvg = firstHalf.reduce((s, m) => s + m.confidence, 0) / firstHalf.length
    const secondAvg = secondHalf.reduce((s, m) => s + m.confidence, 0) / secondHalf.length

    let trend: DriftReport['trend'] = 'stable'
    if (secondAvg < firstAvg * 0.85) trend = 'degrading'
    else if (secondAvg > firstAvg * 1.15) trend = 'improving'

    return {
      model,
      period: '5min',
      avgConfidence: Math.round(avgConfidence * 1000) / 1000,
      avgProcessingTime: Math.round(avgProcessingTime * 10) / 10,
      detectionRate: Math.round(detectionRate * 1000) / 1000,
      trend,
      sampleCount: recentMetrics.length,
    }
  }

  getAllReports(): DriftReport[] {
    const models = [...new Set(this.metrics.map(m => m.model))]
    return models.map(model => this.getReport(model))
  }

  reset() {
    this.metrics = []
  }
}

export const driftMonitor = new DriftMonitor()
export type { DriftReport, DetectionMetric }
