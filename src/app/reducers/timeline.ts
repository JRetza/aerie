/**
 * Copyright 2018, by the California Institute of Technology. ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged.
 * Any commercial use must be negotiated with the Office of Technology Transfer at the California Institute of Technology.
 * This software may be subject to U.S. export control laws and regulations.
 * By accepting this document, the user agrees to comply with all applicable U.S. export laws and regulations.
 * User has the responsibility to obtain export licenses, or other export authority as may be required
 * before exporting such information to foreign countries or providing access to foreign persons
 */

import { omit } from 'lodash';

import { createFeatureSelector, createSelector } from '@ngrx/store';

import {
  FetchGraphDataSuccess,
  RemoveBands,
  SourceExplorerAction,
  SourceExplorerActionTypes,
} from './../actions/source-explorer';

import {
  SelectBand,
  SettingsUpdateAllBands,
  SettingsUpdateBand,
  SortBands,
  TimelineAction,
  TimelineActionTypes,
} from '../actions/timeline';

import {
  updateSortOrder,
  updateTimeRanges,
} from './../shared/util';

import {
  RavenActivityBand,
  RavenActivityPoint,
  RavenBand,
  RavenTimeRange,
} from './../shared/models';

// Timeline State Interface.
export interface TimelineState {
  bands: RavenBand[];
  labelWidth: number;
  maxTimeRange: RavenTimeRange;
  overlayMode: boolean;
  selectedBandId: string;
  viewTimeRange: RavenTimeRange;
}

// Timeline Initial State.
export const initialState: TimelineState = {
  bands: [],
  labelWidth: 99,
  maxTimeRange: { end: 0, start: 0 },
  overlayMode: false,
  selectedBandId: '',
  viewTimeRange: { end: 0, start: 0 },
};

/**
 * Reducer.
 * If a case takes more than one line then it should be in it's own helper function.
 */
export function reducer(state: TimelineState = initialState, action: SourceExplorerAction | TimelineAction): TimelineState {
  switch (action.type) {
    case SourceExplorerActionTypes.FetchGraphDataSuccess:
      return addBands(state, action);
    case SourceExplorerActionTypes.RemoveBands:
      return removeBands(state, action);
    case TimelineActionTypes.SelectBand:
      return selectBand(state, action);
    case TimelineActionTypes.SettingsUpdateAllBands:
      return settingsUpdateAllBands(state, action);
    case TimelineActionTypes.SettingsUpdateBand:
      return settingsUpdateBand(state, action);
    case TimelineActionTypes.SortBands:
      return sortBands(state, action);
    case TimelineActionTypes.UpdateViewTimeRange:
      return { ...state, viewTimeRange: { ...action.viewTimeRange } };
    default:
      return state;
  }
}

/**
 * Reduction Helper. Called when reducing the 'FetchGraphDataSuccess' action.
 * Associates each band with the given source id, and adds any new band.
 * This action is defined in the sourceExplorer actions.
 */
export function addBands(state: TimelineState, action: FetchGraphDataSuccess): TimelineState {
  const bands = state.bands
    // 1. Map over existing bands and add any points from the action.
    .map((band: RavenBand) => {
      // If there is a band that has new points, then add the points and update the corresponding source id.
      if (action.bandData.updateActivityBands[band.id]) {
        return {
          ...band,
          points: (band as RavenActivityBand).points.concat(action.bandData.updateActivityBands[band.id].points),
          sourceIds: {
            ...band.sourceIds,
            [action.source.id]: action.source.name,
          },
        } as RavenActivityBand;
      }

      return band;
    })
    // 2. Add and new bands from the action.
    //    Make sure sortOrder is set here. Assumes new bands are appended to the end of the '0' container.
    .concat(action.bandData.newBands.map((band: RavenBand, index: number) => {
      return {
        ...band,
        containerId: '0',
        sortOrder: state.bands.filter(b => b.containerId === '0').length + index,
        sourceIds: {
          ...band.sourceIds,
          [action.source.id]: action.source.name,
        },
      };
    }));

  return {
    ...state,
    bands,
    ...updateTimeRanges(state.viewTimeRange, bands),
  };
}

/**
 * Reduction Helper. Called when reducing the 'RemoveBands' action.
 * This action is defined in the sourceExplorer actions.
 *
 * When we remove bands we also have to account for the selectedBand.
 * If bands is empty, or if we remove a band that is selected, make sure to set selectedBand to null.
 */
export function removeBands(state: TimelineState, action: RemoveBands): TimelineState {
  let bands = state.bands
    // 1. Filter any bands with an id in removeBandIds.
    .filter((band: RavenBand) => {
      return !action.remove.bandIds.includes(band.id);
    })
    // 2. Remove points from bands with an id in removePointsBandIds.
    .map((band: RavenBand) => {
      // Remove points from bands with ids in the bandsIds list, and also update the source ids.
      if (action.remove.pointsBandIds.includes(band.id)) {
        return {
          ...band,
          points: (band as RavenActivityBand).points.filter((point: RavenActivityPoint) => point.sourceId !== action.source.id),
          sourceIds: omit(band.sourceIds, action.source.id),
        } as RavenActivityBand;
      }

      // Otherwise if the band id is not included in the bandIds list, then return it as-is.
      return band;
    });

  // Update the sort order of all the bands per each container.
  bands = updateSortOrder(bands);

  return {
    ...state,
    bands,
    selectedBandId: state.selectedBandId && action.remove.bandIds.includes(state.selectedBandId) ? '' : state.selectedBandId,
    ...updateTimeRanges(state.viewTimeRange, bands),
  };
}

/**
 * Reduction Helper. Called when reducing the 'SelectBand' action.
 *
 * If we click on a band that's already selected, just de-select it.
 */
export function selectBand(state: TimelineState, action: SelectBand): TimelineState {
  return {
    ...state,
    selectedBandId: action.bandId === state.selectedBandId ? '' : action.bandId,
  };
}

/**
 * Reduction Helper. Called when reducing the 'SettingsUpdateAllBands' action.
 */
export function settingsUpdateAllBands(state: TimelineState, action: SettingsUpdateAllBands): TimelineState {
  return {
    ...state,
    [action.prop]: action.value,
  };
}

/**
 * Reduction Helper. Called when reducing the 'SettingsUpdateBand' action.
 */
export function settingsUpdateBand(state: TimelineState, action: SettingsUpdateBand): TimelineState {
  return {
    ...state,
    bands: state.bands.map((band: RavenBand) => {
      if (state.selectedBandId && state.selectedBandId === band.id) {
        return {
          ...band,
          [action.prop]: action.value,
        };
      }

      return band;
    }),
  };
}

/**
 * Reduction Helper. Called when reducing the 'NewSortOrder' action.
 */
export function sortBands(state: TimelineState, action: SortBands): TimelineState {
  return {
    ...state,
    bands: state.bands.map((band: RavenBand) => {
      if (action.sort[band.id]) {
        return {
          ...band,
          containerId: action.sort[band.id].containerId,
          sortOrder: action.sort[band.id].sortOrder,
        };
      }

      return band;
    }),
  };
}

/**
 * Timeline state selector helper.
 */
export const getTimelineState = createFeatureSelector<TimelineState>('timeline');

/**
 * Create selector helper for selecting state slice.
 *
 * Every reducer module exports selector functions, however child reducers
 * have no knowledge of the overall state tree. To make them usable, we
 * need to make new selectors that wrap them.
 *
 * The createSelector function creates very efficient selectors that are memoized and
 * only recompute when arguments change. The created selectors can also be composed
 * together to select different pieces of state.
 */
export const getBands = createSelector(getTimelineState, (state: TimelineState) => state.bands);
export const getLabelWidth = createSelector(getTimelineState, (state: TimelineState) => state.labelWidth);
export const getMaxTimeRange = createSelector(getTimelineState, (state: TimelineState) => state.maxTimeRange);
export const getOverlayMode = createSelector(getTimelineState, (state: TimelineState) => state.overlayMode);
export const getSelectedBandId = createSelector(getTimelineState, (state: TimelineState) => state.selectedBandId);
export const getViewTimeRange = createSelector(getTimelineState, (state: TimelineState) => state.viewTimeRange);
