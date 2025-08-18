# def nodes_left_to_right(nodes):
#     return sorted(nodes, key=lambda n: (n.pos()[0], n.pos()[1]))

# def nodes_top_to_bottom(nodes):
#     return sorted(nodes, key=lambda n: (n.pos()[1], n.pos()[0]))

# def nodes_reading_order(nodes, row_tol=None):
#     hs = []
#     if row_tol is None:
#         for n in nodes:
#             try:
#                 hs.append(n.get_property("height"))
#             except Exception:
#                 pass
#         avg_h = (sum(hs) / len(hs)) if hs else 60
#         row_tol = max(0.6 * avg_h, 30)

#     by_y = sorted(nodes, key=lambda n: n.pos()[1])
#     rows = []
#     cur_row = []
#     cur_y = None
#     for n in by_y:
#         y = n.pos()[1]
#         if cur_y is None or abs(y - cur_y) <= row_tol:
#             cur_row.append(n)
#             cur_y = y if cur_y is None else (0.7 * cur_y + 0.3 * y)
#         else:
#             rows.append(cur_row)
#             cur_row = [n]
#             cur_y = y
#     if cur_row:
#         rows.append(cur_row)

#     ordered = []
#     for row in rows:
#         ordered.extend(sorted(row, key=lambda n: n.pos()[0]))
#     return ordered
