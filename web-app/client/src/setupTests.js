// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import { TextDecoder, TextEncoder } from 'util';

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// React Router v7 exposes an optional DOM entry that CRA's Jest resolver does
// not resolve through the package export map. The app only uses core routing
// APIs, so map that entry to the core package for tests.
jest.mock('react-router/dom', () => require('react-router'), { virtual: true });
