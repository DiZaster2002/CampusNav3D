/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SpatialPlanList } from '../models/SpatialPlanList';
import type { SpatialPlanStatus } from '../models/SpatialPlanStatus';
import type { SpatialPlanUpload } from '../models/SpatialPlanUpload';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PlansService {
    /**
     * GET /api/plans/
     * Devuelve la lista completa de planos registrados y sus estados actuales.
     * @returns SpatialPlanList
     * @throws ApiError
     */
    public static plansList(): CancelablePromise<Array<SpatialPlanList>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/plans/',
        });
    }
    /**
     * POST /api/plans//approve/
     * Convierte el draft_data (o la versión editada) en objetos GIS reales (Space)
     * y marca el plano como APPROVED.
     * @param id
     * @returns any No response body
     * @throws ApiError
     */
    public static plansApproveCreate(
        id: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/plans/{id}/approve/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * POST /api/plans//reject/
     * Marca un plano como REJECTED indicando el motivo.
     * @param id
     * @returns any No response body
     * @throws ApiError
     */
    public static plansRejectCreate(
        id: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/plans/{id}/reject/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * GET /api/plans//status/
     * Endpoint ligero para que el Frontend haga Polling sobre el progreso.
     * @param id
     * @returns SpatialPlanStatus
     * @throws ApiError
     */
    public static plansStatusRetrieve(
        id: number,
    ): CancelablePromise<SpatialPlanStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/plans/{id}/status/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * POST /api/plans/upload/
     * Recibe la imagen del plano y encola de forma explícita la tarea en Celery.
     * Responde HTTP 202 Accepted de inmediato.
     * @param formData
     * @returns SpatialPlanUpload
     * @throws ApiError
     */
    public static plansUploadCreate(
        formData: SpatialPlanUpload,
    ): CancelablePromise<SpatialPlanUpload> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/plans/upload/',
            formData: formData,
            mediaType: 'multipart/form-data',
        });
    }
}
