// Code generated by MockGen. DO NOT EDIT.
// Source: sigs.k8s.io/aws-load-balancer-controller/pkg/networking (interfaces: NodeInfoProvider)

// Package networking is a generated GoMock package.
package networking

import (
	context "context"
	reflect "reflect"

	types "github.com/aws/aws-sdk-go-v2/service/ec2/types"
	gomock "github.com/golang/mock/gomock"
	v1 "k8s.io/api/core/v1"
	types0 "k8s.io/apimachinery/pkg/types"
)

// MockNodeInfoProvider is a mock of NodeInfoProvider interface.
type MockNodeInfoProvider struct {
	ctrl     *gomock.Controller
	recorder *MockNodeInfoProviderMockRecorder
}

// MockNodeInfoProviderMockRecorder is the mock recorder for MockNodeInfoProvider.
type MockNodeInfoProviderMockRecorder struct {
	mock *MockNodeInfoProvider
}

// NewMockNodeInfoProvider creates a new mock instance.
func NewMockNodeInfoProvider(ctrl *gomock.Controller) *MockNodeInfoProvider {
	mock := &MockNodeInfoProvider{ctrl: ctrl}
	mock.recorder = &MockNodeInfoProviderMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockNodeInfoProvider) EXPECT() *MockNodeInfoProviderMockRecorder {
	return m.recorder
}

// FetchNodeInstances mocks base method.
func (m *MockNodeInfoProvider) FetchNodeInstances(arg0 context.Context, arg1 []*v1.Node) (map[types0.NamespacedName]*types.Instance, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "FetchNodeInstances", arg0, arg1)
	ret0, _ := ret[0].(map[types0.NamespacedName]*types.Instance)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// FetchNodeInstances indicates an expected call of FetchNodeInstances.
func (mr *MockNodeInfoProviderMockRecorder) FetchNodeInstances(arg0, arg1 interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "FetchNodeInstances", reflect.TypeOf((*MockNodeInfoProvider)(nil).FetchNodeInstances), arg0, arg1)
}