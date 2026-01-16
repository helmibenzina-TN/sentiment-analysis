import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import {
  AnalysisResponse,
  SmartphoneScore,
  HistoryResponse,
  PerformanceRankingsResponse,
  AllPerformanceCategoriesResponse
} from '../models/models';

@Injectable({
  providedIn: 'root'
})
export class Api {
  private readonly API_URL = '/api';

  constructor(private http: HttpClient) { }

  analyzeSentiment(product1: string, product2?: string): Observable<AnalysisResponse> {
    let params = new HttpParams().set('product1', product1);
    if (product2) {
      params = params.set('product2', product2);
    }

    return this.http.get<AnalysisResponse>(`${this.API_URL}/sentiment/analyze`, { params })
      .pipe(catchError(this.handleError));
  }

  getTopSmartphones(limit: number = 10): Observable<{ smartphones: SmartphoneScore[] }> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<{ smartphones: SmartphoneScore[] }>(`${this.API_URL}/smartphones/top`, { params })
      .pipe(catchError(this.handleError));
  }

  getSearchHistory(page: number = 1, perPage: number = 20): Observable<HistoryResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get<HistoryResponse>(`${this.API_URL}/history`, { params })
      .pipe(catchError(this.handleError));
  }

  getRecentHistory(limit: number = 5): Observable<{ recent_searches: string[] }> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<{ recent_searches: string[] }>(`${this.API_URL}/history/recent`, { params })
      .pipe(catchError(this.handleError));
  }

  getPerformanceRankings(category: string = 'overall', limit: number = 10): Observable<PerformanceRankingsResponse> {
    const params = new HttpParams()
      .set('category', category)
      .set('limit', limit.toString());

    return this.http.get<PerformanceRankingsResponse>(`${this.API_URL}/performance/rankings`, { params })
      .pipe(catchError(this.handleError));
  }

  getAllPerformanceCategories(limit: number = 10): Observable<AllPerformanceCategoriesResponse> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<AllPerformanceCategoriesResponse>(`${this.API_URL}/performance/all-categories`, { params })
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any): Observable<never> {
    let errorMessage = 'An error occurred';

    if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else if (error.error && error.error.error) {
      errorMessage = error.error.error;
    } else if (error.message) {
      errorMessage = error.message;
    }

    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
