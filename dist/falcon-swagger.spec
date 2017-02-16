%define name falcon-swagger
%define release 1

Summary: Swagger support for falcon APIs  
Name: %{name}
Version: %{version}
Release: %{release}
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Data Insight <dig@rakuten.com>
Requires: falcon 
BuildRequires: python-devel

%description
Provides Swagger documentation for Falcon APIs

%prep
#%setup -n %{name}
cp -r %{_jenkins_workspace} %{_builddir}/%{name}

%build
cd %{name}
python setup.py build

%install
cd %{name}
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf ${_builddir}/%{name}
