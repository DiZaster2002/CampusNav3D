/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PatchedSpace } from '../models/PatchedSpace';
import type { Space } from '../models/Space';
import type { SpaceList } from '../models/SpaceList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SpacesService {
    /**
     * @returns SpaceList
     * @throws ApiError
     */
    public static spacesList(): CancelablePromise<SpaceList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/spaces/',
        });
    }
    /**
     * @param requestBody
     * @returns Space
     * @throws ApiError
     */
    public static spacesCreate(
        requestBody?: Space,
    ): CancelablePromise<Space> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/spaces/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this space.
     * @returns Space
     * @throws ApiError
     */
    public static spacesRetrieve(
        id: number,
    ): CancelablePromise<Space> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/spaces/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * @param id A unique integer value identifying this space.
     * @param requestBody
     * @returns Space
     * @throws ApiError
     */
    public static spacesUpdate(
        id: number,
        requestBody?: Space,
    ): CancelablePromise<Space> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/spaces/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this space.
     * @param requestBody
     * @returns Space
     * @throws ApiError
     */
    public static spacesPartialUpdate(
        id: number,
        requestBody?: PatchedSpace,
    ): CancelablePromise<Space> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/spaces/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param id A unique integer value identifying this space.
     * @returns void
     * @throws ApiError
     */
    public static spacesDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/spaces/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
