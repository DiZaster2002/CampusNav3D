/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RouteService {
    /**
     * Endpoint REST para el cálculo de itinerarios interiores.
     *
     * GET /api/route/?start_space_id=1&target_space_id=5&preference=accessible
     * @returns any No response body
     * @throws ApiError
     */
    public static routeRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/route/',
        });
    }
}
