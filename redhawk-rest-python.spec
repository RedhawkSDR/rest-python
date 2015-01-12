#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK core.
#
# REDHAWK core is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK core is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
%define _prefix /var/redhawk/web
%define _app %{_prefix}/rest-python
%define _supervisor /etc/redhawk-web/supervisor.d
%define _nginx /etc/nginx/conf.d/redhawk-sites

Prefix:         %{_prefix}
Name:		redhawk-rest-python
Version:	2.1.0
Release:	1%{?dist}
Summary:	A REDHAWK REST application that exposes the entire domain.

License:	GPL
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Source0:        %{name}-%{version}.tar.gz

Requires:       python
Requires:       redhawk >= 1.10
Requires:       redhawk-devel
Requires:       bulkioInterfaces
Requires:       redhawk-web
Requires:       rhweb-python-tornado
Requires:	python-futures

%description
%{summary}
 * Commit: __REVISION__
 * Source Date/Time: __DATETIME__

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT%{_app}
cp pyrest.py         $RPM_BUILD_ROOT%{_app}

mkdir -p $RPM_BUILD_ROOT%{_app}/model/_utils
cp model/*.py        $RPM_BUILD_ROOT%{_app}/model
cp model/_utils/*.py $RPM_BUILD_ROOT%{_app}/model/_utils


mkdir -p $RPM_BUILD_ROOT%{_app}/rest
cp rest/*.py $RPM_BUILD_ROOT%{_app}/rest

cp start.sh          $RPM_BUILD_ROOT%{_app}

mkdir -p $RPM_BUILD_ROOT%{_supervisor}
cp deploy/rest-python-supervisor.conf $RPM_BUILD_ROOT%{_supervisor}/redhawk-rest-python.conf

mkdir -p $RPM_BUILD_ROOT%{_nginx}/redhawk-sites
cp deploy/rest-python-nginx.conf $RPM_BUILD_ROOT%{_nginx}/rest-python.enabled

%clean
rm -rf %{buildroot}

%files
%defattr(-,redhawk,redhawk,-)
%dir %{_app}
%{_app}/start.sh

%{_app}/pyrest.py
%{_app}/pyrest.pyc
%{_app}/pyrest.pyo
%{_app}/model
%{_app}/model/_utils
%{_app}/rest

%defattr(-,root,root,-)
%{_nginx}/rest-python.enabled
%{_supervisor}/redhawk-rest-python.conf

