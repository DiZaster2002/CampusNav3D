/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NavigationEdge } from '../models/NavigationEdge';
import type { NavigationEdgeList } from '../models/NavigationEdgeList';
import type { PatchedNavigationEdge } from '../models/PatchedNavigationEdge';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EdgesService {
    /**
     * @returns NavigationEdgeList
     * @throws ApiError
     */
    public static edgesList(): CancelablePromise<NavigationEdgeList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/edges/',
        });
    }
    /**
     * @param requestBody
     * @returns NavigationEdge
     * @throws ApiError
     */
    public static edgesCreate(
        requestBody?: NavigationEdge,
    ): CancelablePromise<NavigationEdge> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/edges/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this navigation edge.
     * @returns NavigationEdge
     * @throws ApiError
     */
    public static edgesRetrieve(
        id: number,
    ): CancelablePromise<NavigationEdge> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/edges/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this navigation edge.
     * @param requestBody
     * @returns NavigationEdge
     * @throws ApiError
     */
    public static edgesUpdate(
        id: number,
        requestBody?: NavigationEdge,
    ): CancelablePromise<NavigationEdge> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/edges/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this navigation edge.
     * @param requestBody
     * @returns NavigationEdge
     * @throws ApiError
     */
    public static edgesPartialUpdate(
        id: number,
        requestBody?: PatchedNavigationEdge,
    ): CancelablePromise<NavigationEdge> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/edges/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this navigation edge.
     * @returns void
     * @throws ApiError
     */
    public static edgesDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/edges/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
