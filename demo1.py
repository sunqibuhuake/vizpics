import c4d
from math import sin, cos, radians, pi, atan, tan

#北京经纬度
bjLocation = (39.904213937233365,116.40741292387247)
#其他亚洲各国经纬度
data = [
    (35.672511, 139.75842),
    (47.921378, 106.90554),
    (21.033333, 105.85),
    (17.962769, 102.614429),
    (11.558831, 104.917445),
    (16.8, 96.15),
    (13.82031, 100.66471),
    (3.139003, 101.686855),
    (4.890278, 114.942222),
    (-6.211544, 106.845172),
    (-8.558458, 125.578151),
    (14.599512, 120.984219),
    (27.702871, 85.318244),
    (27.466667, 89.641667),
    (23.709921, 90.407143),
    (33.718151, 73.060547),
    (6.927079, 79.861243),
    (35.696111, 51.423056),
    (34.528455, 69.171703),
    (25.280282, 51.522476),
    (26.216667, 50.583333),
    (24.466667, 54.366667),
    (24.711667, 46.724167),
    (23.614167, 58.590833),
    (15.352029, 44.207456),
    (33.33248, 44.418399),
    (25.406880020609538,55.43254852294922),
    (33.51592312227881, 36.31359100341797),
    (39.92077, 32.85411),
    (40.183333, 44.516667),
    (41.709981, 44.792998),
    (40.43495, 49.867623),
    (41.266667, 69.216667),
    (37.950197, 58.380223),
    (42.870022, 74.587883)
]

#三次贝塞尔曲线计算函数
def b3p0(t , p):
    k = 1 - t
    return k * k * k * p
def b3p1(t,p):
    k = 1 - t
    return 3 * k * k * t * p
def b3p2(t,p):
    k = 1 - t
    return 3 * k * t * t * p
def b3p3(t,p):
    return t * t * t * p
def b3(t, p0, p1, p2, p3):
    return b3p0(t, p0) + b3p1(t, p1) + b3p2(t, p2) + b3p3(t, p3)

class CubicBezierCurve3(object):
    def __init__(self, v0, v1, v2, v3):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
    def getPoint(self, t):
        x = b3(t, self.v0.x, self.v1.x, self.v2.x, self.v3.x)
        y = b3(t, self.v0.y, self.v1.y, self.v2.y, self.v3.y)
        z = b3(t, self.v0.z, self.v1.z, self.v2.z, self.v3.z)
        return c4d.Vector(x,y,z)
    def getPoints(self, divisions = 5):
        arr = [];
        for i in range(divisions):
            arr.append(self.getPoint( ( i + 0.0 ) / divisions))
        return arr



#经纬度转空间坐标
def geo2pos(lat_deg,lon_deg, rad):
    lat = radians(lat_deg)
    lon = radians(lon_deg)
    alt = 0.0
    f  = 0.0
    ls = atan((1 - f)**2 * tan(lat))
    x = rad * cos(lat) * cos(lon) + alt * cos(lat) * cos(lon)
    z = rad * cos(lat) * sin(lon) + alt * cos(lat) * sin(lon)
    y = rad * sin(lat) + alt * sin(lat)
    return c4d.Vector(x, y,z)


#获取两点间曲线
def getCurveFromLocation(lat1,lon1,lat2,lon2):
    lon2 += 10
    if lon2 > 180:
        lon2 -= 360

    #项目中地区半径为100cm
    earthRadius = 100
    controlPointRadius = 120

    v1lat = 0
    v1lon = 0
    v2lat = 0
    v2lon = 0
    interval = 4

    deltaLat = lat1 - lat2
    v1lat = lat1 - deltaLat / interval
    v2lat = lat2 + deltaLat / interval


    if lon1 * lon2 > 0:
        deltaLon = lon1 - lon2
        v1lon = lon1 - deltaLon / interval
        v2lon = lon2 + deltaLon / interval
    else:
        if abs(lon1) + abs(lon2) > 180:
            deltaLon = 360 - abs(lon1) - abs(lon2)
            if lon1 > 0:
                v1lon = lon1 + deltaLon / interval
                v2lon = lon2 - deltaLon / interval
                if v1lon > 180:
                    v1lon -= 360
                if v2lon < -180 :
                    v2lon += 360
            else:
                v2lon = lon1 + deltaLon / interval
                v1lon = lon2 - deltaLon / interval
                if v2lon > 180:
                    v2lon -= 360
                if v1lon < -180 :
                    v1lon += 360

        else:
            deltaLon = lon1 - lon2
            v1lon = lon1 - deltaLon / interval
            v2lon = lon2 + deltaLon / interval



    vertex0 = geo2pos(lat1, lon1, earthRadius)
    vertex1 = geo2pos(v1lat, v1lon, controlPointRadius)
    vertex2 = geo2pos(v2lat, v2lon, controlPointRadius)
    vertex3 = geo2pos(lat2, lon2, earthRadius)

    curve = CubicBezierCurve3(vertex0,vertex1,vertex2,vertex3)
    pointsArr = curve.getPoints(300)
    return pointsArr


#获取thinking particle
tp = doc.GetParticleSystem()

def createPaths(arr, center):
    pathsArr = []
    l = len(arr)
    for i in range(l):
        path = getCurveFromLocation(center[0], center[1], arr[i][0], arr[i][1])
        pathsArr.append(path)
    return pathsArr

#曲线总数
pathsNum = len(data)

#曲线数组
pathsArr = createPaths(data, bjLocation)

def main():
    #获取当前帧
    frameIndex = doc.GetTime().GetFrame(doc.GetFps())
    if frameIndex > 0:
        for i in range(pathsNum):
            tp.SetPosition(i, pathsArr[i][frameIndex - 1])
