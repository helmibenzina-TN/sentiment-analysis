import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api } from '../services/api';
import { AllPerformanceCategoriesResponse } from '../models/models';

@Component({
  selector: 'app-performance',
  imports: [CommonModule],
  templateUrl: './performance.html',
  styleUrl: './performance.css',
})
export class Performance implements OnInit {
  performanceData: AllPerformanceCategoriesResponse | null = null;
  loading = false;
  selectedCategory = 'overall';

  constructor(private apiService: Api) { }

  ngOnInit() {
    this.loadPerformanceData();
  }

  loadPerformanceData() {
    this.loading = true;
    this.apiService.getAllPerformanceCategories(10).subscribe({
      next: (response) => {
        this.performanceData = response;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading performance data:', err);
        this.loading = false;
      }
    });
  }

  selectCategory(category: string) {
    this.selectedCategory = category;
  }

  getCategoryData() {
    if (!this.performanceData) return [];

    switch (this.selectedCategory) {
      case 'overall': return this.performanceData.overall;
      case 'performance': return this.performanceData.performance;
      case 'battery': return this.performanceData.battery;
      case 'camera': return this.performanceData.camera;
      case 'value': return this.performanceData.value;
      default: return [];
    }
  }
}
