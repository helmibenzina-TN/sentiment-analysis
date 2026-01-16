import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Api } from '../services/api';
import { SmartphoneScore } from '../models/models';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  searchForm: FormGroup;
  topSmartphones: SmartphoneScore[] = [];
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private apiService: Api,
    private router: Router
  ) {
    this.searchForm = this.fb.group({
      product1: [''],
      product2: ['']
    });
  }

  ngOnInit() {
    this.loadTopSmartphones();
  }

  loadTopSmartphones() {
    this.apiService.getTopSmartphones(10).subscribe({
      next: (response) => {
        this.topSmartphones = response.smartphones;
      },
      error: (err) => {
        console.error('Error loading top smartphones:', err);
      }
    });
  }

  onSearch() {
    const product1 = this.searchForm.value.product1?.trim();
    if (!product1) {
      this.error = 'Please enter at least one smartphone name';
      return;
    }

    const product2 = this.searchForm.value.product2?.trim();

    this.router.navigate(['/results'], {
      queryParams: {
        product1,
        ...(product2 && { product2 })
      }
    });
  }

  analyzePhone(phoneName: string) {
    this.router.navigate(['/results'], {
      queryParams: { product1: phoneName }
    });
  }
}
