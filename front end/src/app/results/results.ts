import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Api } from '../services/api';
import { AnalysisResponse, SentimentResult } from '../models/models';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

@Component({
  selector: 'app-results',
  imports: [CommonModule],
  templateUrl: './results.html',
  styleUrl: './results.css',
})
export class Results implements OnInit, AfterViewInit {
  product1Name = '';
  product2Name = '';
  product1Results: SentimentResult | null = null;
  product2Results: SentimentResult | null = null;
  loading = false;
  error = '';

  private chart1: Chart | null = null;
  private chart2: Chart | null = null;

  constructor(
    private route: ActivatedRoute,
    private apiService: Api
  ) { }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.product1Name = params['product1'];
      this.product2Name = params['product2'];

      if (this.product1Name) {
        this.analyzeProducts();
      }
    });
  }

  ngAfterViewInit() {
    // Charts will be created after data is loaded
  }

  analyzeProducts() {
    this.loading = true;
    this.error = '';

    this.apiService.analyzeSentiment(this.product1Name, this.product2Name).subscribe({
      next: (response: AnalysisResponse) => {
        this.product1Results = response.product1.results;
        if (response.product2) {
          this.product2Results = response.product2.results;
        }
        this.loading = false;

        // Create charts after data is loaded
        setTimeout(() => this.createCharts(), 100);
      },
      error: (err) => {
        this.error = err.message || 'Failed to analyze sentiment';
        this.loading = false;
      }
    });
  }

  createCharts() {
    if (this.product1Results) {
      this.createSentimentChart('sentimentChart1', this.product1Results);
    }
    if (this.product2Results) {
      this.createSentimentChart('sentimentChart2', this.product2Results);
    }
  }

  createSentimentChart(canvasId: string, results: SentimentResult) {
    const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Destroy existing chart if any
    if (canvasId === 'sentimentChart1' && this.chart1) {
      this.chart1.destroy();
    }
    if (canvasId === 'sentimentChart2' && this.chart2) {
      this.chart2.destroy();
    }

    const config: ChartConfiguration = {
      type: 'pie',
      data: {
        labels: ['Positive', 'Negative', 'Neutral'],
        datasets: [{
          data: [
            results.overall_sentiment.positive,
            results.overall_sentiment.negative,
            results.overall_sentiment.neutral
          ],
          backgroundColor: [
            'rgba(52, 199, 89, 0.8)',
            'rgba(255, 59, 48, 0.8)',
            'rgba(142, 142, 147, 0.8)'
          ],
          borderColor: [
            'rgba(52, 199, 89, 1)',
            'rgba(255, 59, 48, 1)',
            'rgba(142, 142, 147, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              font: {
                size: 12,
                family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
              }
            }
          },
          title: {
            display: true,
            text: 'Overall Sentiment Distribution',
            font: {
              size: 16,
              weight: 600,
              family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
            },
            padding: {
              top: 10,
              bottom: 20
            }
          }
        }
      }
    };

    const chart = new Chart(ctx, config);

    if (canvasId === 'sentimentChart1') {
      this.chart1 = chart;
    } else {
      this.chart2 = chart;
    }
  }

  getSentimentPercentage(results: SentimentResult, type: 'positive' | 'negative' | 'neutral'): number {
    const total = results.overall_sentiment.positive + results.overall_sentiment.negative + results.overall_sentiment.neutral;
    if (total === 0) return 0;
    return (results.overall_sentiment[type] / total) * 100;
  }

  getAspectKeys(results: SentimentResult): string[] {
    return Object.keys(results.aspect_sentiments);
  }

  ngOnDestroy() {
    if (this.chart1) this.chart1.destroy();
    if (this.chart2) this.chart2.destroy();
  }
}
