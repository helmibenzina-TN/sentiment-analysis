import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Api } from '../services/api';
import { SearchHistoryItem } from '../models/models';

@Component({
  selector: 'app-history',
  imports: [CommonModule],
  templateUrl: './history.html',
  styleUrl: './history.css',
})
export class History implements OnInit {
  history: SearchHistoryItem[] = [];
  loading = false;
  currentPage = 1;
  totalPages = 1;
  hasNext = false;
  hasPrev = false;

  constructor(
    private apiService: Api,
    private router: Router
  ) { }

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory(page: number = 1) {
    this.loading = true;
    this.apiService.getSearchHistory(page, 20).subscribe({
      next: (response) => {
        this.history = response.history;
        this.currentPage = response.current_page;
        this.totalPages = response.pages;
        this.hasNext = response.has_next;
        this.hasPrev = response.has_prev;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading history:', err);
        this.loading = false;
      }
    });
  }

  reanalyze(productName: string) {
    this.router.navigate(['/results'], {
      queryParams: { product1: productName }
    });
  }

  nextPage() {
    if (this.hasNext) {
      this.loadHistory(this.currentPage + 1);
    }
  }

  prevPage() {
    if (this.hasPrev) {
      this.loadHistory(this.currentPage - 1);
    }
  }
}
