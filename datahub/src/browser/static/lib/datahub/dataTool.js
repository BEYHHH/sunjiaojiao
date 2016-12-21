! function(e, t) {
	"object" == typeof exports && "object" == typeof module ? module.exports = t(require("echarts")) : "function" == typeof define && define.amd ? define(["echarts"], t) : "object" == typeof exports ? exports.dataTool = t(require("echarts")) : (e.echarts = e.echarts || {}, e.echarts.dataTool = t(e.echarts))
}(this, function(e) {
	return function(e) {
		function t(o) {
			if(r[o]) return r[o].exports;
			var n = r[o] = {
				exports: {},
				id: o,
				loaded: !1
			};
			return e[o].call(n.exports, n, n.exports, t), n.loaded = !0, n.exports
		}
		var r = {};
		return t.m = e, t.c = r, t.p = "", t(0)
	}([function(e, t, r) {
		var o;
		o = function(e) {
			var t = r(1);
			return t.dataTool = {
				version: "1.0.0",
				gexf: r(5),
				prepareBoxplotData: r(6)
			}, t.dataTool
		}.call(t, r, t, e), !(void 0 !== o && (e.exports = o))
	}, function(t, r) {
		t.exports = e
	}, , , , function(e, t, r) {
		var o;
		o = function(e) {
			"use strict";

			function t(e) {
				var t;
				if("string" == typeof e) {
					var r = new DOMParser;
					t = r.parseFromString(e, "text/xml")
				} else t = e;
				if(!t || t.getElementsByTagName("parsererror").length) return null;
				var i = l(t, "gexf");
				if(!i) return null;
				for(var u = l(i, "graph"), s = o(l(u, "attributes")), c = {}, f = 0; f < s.length; f++) c[s[f].id] = s[f];
				return {
					nodes: n(l(u, "nodes"), c),
					links: a(l(u, "edges"))
				}
			}

			function o(e) {
				return e ? s.map(u(e, "attribute"), function(e) {
					return {
						id: i(e, "id"),
						title: i(e, "title"),
						type: i(e, "type")
					}
				}) : []
			}

			function n(e, t) {
				return e ? s.map(u(e, "node"), function(e) {
					var r = i(e, "id"),
						o = i(e, "label"),
						n = {
							id: r,
							name: o,
							itemStyle: {
								normal: {}
							}
						},
						a = l(e, "viz:size"),
						s = l(e, "viz:position"),
						c = l(e, "viz:color"),
						f = l(e, "attvalues");
					if(a && (n.symbolSize = parseFloat(i(a, "value"))), s && (n.x = parseFloat(i(s, "x")), n.y = parseFloat(i(s, "y"))), c && (n.itemStyle.normal.color = "rgb(" + [0 | i(c, "r"), 0 | i(c, "g"), 0 | i(c, "b")].join(",") + ")"), f) {
						var p = u(f, "attvalue");
						n.attributes = {};
						for(var v = 0; v < p.length; v++) {
							var d = p[v],
								g = i(d, "for"),
								h = i(d, "value"),
								b = t[g];
							if(b) {
								switch(b.type) {
									case "integer":
									case "long":
										h = parseInt(h, 10);
										break;
									case "float":
									case "double":
										h = parseFloat(h);
										break;
									case "boolean":
										h = "true" == h.toLowerCase()
								}
								n.attributes[g] = h
							}
						}
					}
					return n
				}) : []
			}

			function a(e) {
				return e ? s.map(u(e, "edge"), function(e) {
					var t = i(e, "id"),
						r = i(e, "label"),
						o = i(e, "source"),
						n = i(e, "target"),
						a = {
							id: t,
							name: r,
							source: o,
							target: n,
							lineStyle: {
								normal: {}
							}
						},
						u = a.lineStyle.normal,
						s = l(e, "viz:thickness"),
						c = l(e, "viz:color");
					return s && (u.width = parseFloat(s.getAttribute("value"))), c && (u.color = "rgb(" + [0 | i(c, "r"), 0 | i(c, "g"), 0 | i(c, "b")].join(",") + ")"), a
				}) : []
			}

			function i(e, t) {
				return e.getAttribute(t)
			}

			function l(e, t) {
				for(var r = e.firstChild; r;) {
					if(1 == r.nodeType && r.nodeName.toLowerCase() == t.toLowerCase()) return r;
					r = r.nextSibling
				}
				return null
			}

			function u(e, t) {
				for(var r = e.firstChild, o = []; r;) r.nodeName.toLowerCase() == t.toLowerCase() && o.push(r), r = r.nextSibling;
				return o
			}
			var s = r(1).util;
			return {
				parse: t
			}
		}.call(t, r, t, e), !(void 0 !== o && (e.exports = o))
	}, function(e, t, r) {
		var o;
		o = function(e) {
			var t = r(7),
				o = r(1).number;
			return function(e, r) {
				r = r || [];
				for(var n = [], a = [], i = [], l = r.boundIQR, u = 0; u < e.length; u++) {
					i.push(u + "");
					var s = o.asc(e[u].slice()),
						c = t(s, .25),
						f = t(s, .5),
						p = t(s, .75),
						v = p - c,
						d = "none" === l ? s[0] : c - (null == l ? 1.5 : l) * v,
						g = "none" === l ? s[s.length - 1] : p + (null == l ? 1.5 : l) * v;
					n.push([d, c, f, p, g]);
					for(var h = 0; h < s.length; h++) {
						var b = s[h];
						if(d > b || b > g) {
							var x = [u, b];
							"vertical" === r.layout && x.reverse(), a.push(x)
						}
					}
				}
				return {
					boxData: n,
					outliers: a,
					axisData: i
				}
			}
		}.call(t, r, t, e), !(void 0 !== o && (e.exports = o))
	}, function(e, t, r) {
		var o;
		o = function(e) {
			return function(e, t) {
				var r = (e.length - 1) * t + 1,
					o = Math.floor(r),
					n = +e[o - 1],
					a = r - o;
				return a ? n + a * (e[o] - n) : n
			}
		}.call(t, r, t, e), !(void 0 !== o && (e.exports = o))
	}])
});